import asyncio

from dotenv import load_dotenv
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.voice_assistant import (
    VoiceAssistant,
)  # có thể thay thế ở chỗ này để có thể sử dụng livestream thay vì chỉ có giọng nói
from livekit.plugins import (
    openai,
    silero,
)  # có rất nhiều lugins khác như alama (hình con cừu của deft)
from api import AssistanceFnc


load_dotenv()


async def entrypoint(ctx: JobContext):
    initial_ctx = llm.ChatContext().append(
        # ở đây sẽ thêm vào một số ngữ cảnh để bắt đầu trợ lý giọng nói AI, tương tự như cách tạo prome mẫu chẳng hạn
        role="system",
        text=(
            "Bạn là trợ lý ảo được tạo ra bởi Livekit. Giao diện của bạn với người dùng là bằng giọng nói.",
            "Bạn nên sử dụng những câu trả lời ngắn gọn và súc tích, và tránh sử dụng những câu không thể phát âm được.",
        ),
    )
    # chỉ định ở đây là chúng ta chỉ muốn kết nối với những bản âm thanh, hiện tại không quan tâm tới video, nhưng cũng có thể quan tâm tới video(stream) ở đây
    await ctx.connect(AutoSubscribe=AutoSubscribe.AUDIO_ONLY)

    fnc_ctx = AssistanceFnc

    # tiếp theo là xác định trợ lý giọng nói của mình
    assistant = VoiceAssistant(
        # chỉ định loại mô hình và phương pháp phát hiện người dùng có đang nói hay không, để biến khi nào nên dừng chúng lại và gửi message tới AI (có vẻ sẽ liên quan tới auto dịch)
        vad=silero.VAD.load(),
        # cái này là chuyển giọng nói thành văn bản???
        stt=openai.STT(),
        # mô hình ngôn ngữ lớn, cũng ko hiểu lắm
        llm=openai.LLM(),
        # chuyển văn bản thành giọng nói
        tts=openai.TTS(),
        chat_ctx=initial_ctx,
        fnc_ctx=fnc_ctx,
    )
    # kết nối tới các chỉ định và thiết lập trước đó tới một phòng, để có thể kết nối tới nhiều phòng cùng một lúc
    assistant.start(ctx.room)

    await asyncio.sleep(1)
    # cái allow là cho phép ngắt lời chào mừng đó bằng bất cứ cách nào ta muốn
    await assistant.say("Hey, how can i help you today?", allow_interruptions=true)


# nếu chạy trực tiếp file này thì sẽ chạy cli trong livekit-> chạy 1 app mới -> app sẽ là 1 worker -> sẽ thực hiện fnc entrypoint
if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))


# luồng hoạt động sẽ là:
# agents muốn connect tới căn phòng entrypoint -> nó sẽ kết nốt tới livekit server -> livekit server sẽ gửi cho agent một công việc (job)
# và khi job được gửi, nó sẽ có một căn phòng liên quan tới nó
# và chúng đang làm là chúng ta đăng ký âm thanh bên trong và chúng ta muốn khởi động trợ lý bên trong căn phòng này
