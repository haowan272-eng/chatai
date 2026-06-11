"""聊天路由：发送消息、查看历史、SSE 流式"""
import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Conversation, Message
from ..schemas import ChatRequest, ChatResponse
from ..dependencies import get_current_user
from ..llm import call_deepseek, call_deepseek_stream, SYSTEM_PROMPT

router = APIRouter(tags=["聊天"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    聊天接口（需登录）— 接入 DeepSeek LLM。
    自动携带历史消息作为上下文，实现多轮对话。
    """
    # --- 1. 找到用户 ---
    user = db.query(User).filter(User.username == current_user).first()

    # --- 2. 找到或创建会话 ---
    conversation = None
    if req.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == req.conversation_id,
            Conversation.user_id == user.id,
        ).first()

    if not conversation:
        conversation = Conversation(user_id=user.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # --- 3. 保存用户消息 ---
    user_msg = Message(content=req.message, role="user", conversation_id=conversation.id)
    db.add(user_msg)
    db.commit()

    # --- 4. 构建 LLM messages（system prompt + 最近 20 条历史 + 当前消息）---
    history_msgs = (
        db.query(Message)
        .filter(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.desc())
        .limit(20)
        .all()
    )
    history_msgs = list(reversed(history_msgs))

    llm_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in history_msgs:
        llm_messages.append({"role": m.role, "content": m.content})

    # --- 5. 调用 DeepSeek ---
    print(f"\n{'='*60}")
    print(f"[USER {current_user}]: {req.message}")
    print(f"{'='*60}")
    answer = await call_deepseek(llm_messages)
    print(f"[AI]: {answer[:200]}")
    print(f"{'='*60}\n")

    # --- 6. 保存助手回答 ---
    assistant_msg = Message(content=answer, role="assistant", conversation_id=conversation.id)
    db.add(assistant_msg)
    db.commit()

    return ChatResponse(answer=answer, conversation_id=conversation.id)


@router.post("/chat/stream")
async def chat_stream(
    req: ChatRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    流式聊天接口（需登录）— SSE 逐 token 推送。
    前端: const es = new EventSource(...) 或用 fetch + ReadableStream
    """
    # --- 1. 找到用户 ---
    user = db.query(User).filter(User.username == current_user).first()

    # --- 2. 找到或创建会话 ---
    conversation = None
    if req.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == req.conversation_id,
            Conversation.user_id == user.id,
        ).first()

    if not conversation:
        conversation = Conversation(user_id=user.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # --- 3. 保存用户消息 ---
    user_msg = Message(content=req.message, role="user", conversation_id=conversation.id)
    db.add(user_msg)
    db.commit()

    # --- 4. 构建 LLM messages ---
    history_msgs = (
        db.query(Message)
        .filter(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.desc())
        .limit(20)
        .all()
    )
    history_msgs = list(reversed(history_msgs))

    llm_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in history_msgs:
        llm_messages.append({"role": m.role, "content": m.content})

    print(f"\n{'='*60}")
    print(f"[USER {current_user}]: {req.message}")
    print(f"{'='*60}")

    async def event_stream():
        full_answer = ""
        try:
            async for token in call_deepseek_stream(llm_messages):
                full_answer += token
                yield f"data: {json.dumps({'t': token})}\n\n"
        except Exception:
            full_answer = full_answer or "服务异常"
        finally:
            # 保存 AI 回复到数据库
            assistant_msg = Message(
                content=full_answer, role="assistant", conversation_id=conversation.id
            )
            db.add(assistant_msg)
            db.commit()
            # 发送完成信号
            yield f"data: {json.dumps({'done': True, 'conversation_id': conversation.id, 'full': full_answer})}\n\n"
            print(f"[AI]: {full_answer[:200]}...")
            print(f"{'='*60}\n")

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # 禁用 nginx 缓冲
        },
    )


@router.get("/history/{conversation_id}")
def history(
    conversation_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """查看某个会话的历史消息（需登录）"""
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .all()
    )
    return [
        {"role": m.role, "content": m.content, "time": m.created_at.isoformat()}
        for m in messages
    ]
