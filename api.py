import enum
from typing import Annotated
from livekit.agents import llm
import logging

logger = logging.getLogger("temperature-control")
logger.setLevel(logging.INFO)


class Zone(enum.Enum):
    LIVING_ROOM = "living_room"
    KITCHEN = "kitchen"
    BEDROOM = "bedroom"
    BATHROOM = "bathroom"
    OFFICE = "office"


# llm sẽ quyết định gọi hàm nào dựa trên mô tả mà chúng ta cung cấp cho họ, ví dụ ở đây là lấy nhiệt độ và thay đổi nhiệt độ
class AssistanceFnc(llm.FunctionContext):
    def __init__(self) -> None:
        super().__init__()
        self.temerature = {
            Zone.LIVING_ROOM: 25,
            Zone.KITCHEN: 20,
            Zone.BEDROOM: 24,
            Zone.BATHROOM: 22,
            Zone.OFFICE: 21,
        }

    # trình tạo python chỉ định hàm mà chúng ta sắp viết có thể được gọi bởi llm của chúng ta
    @llm.ai_callable(description="Get the temperature in a specific room")
    # hàm lấy ra nhiệt độ phòng hiện tại
    def get_temperature(
        self, zone: Annotated[Zone, llm.TypeInfo(description="The specific zone")]
    ):
        # zone sẽ là một chuỗi, ta cần chuyển về enum
        logger.info("Get temp - zone: %s", zone)
        temp = self._temperature[Zone(zone)]
        return f"The temperature in {zone} is {temp} degree"

    # hàm thay đổi nhiệt độ
    @llm.ai_callable(description="Change the temperature in a specific room")
    def set_temperature(
        self,
        zone: Annotated[Zone, llm.TypeInfo(description="The specific zone")],
        temp: Annotated[int, llm.TypeInfo(description="The temperature to set")],
    ):
        logger.info("set temp zone %s, temp %s", zone, temp)
        self._temperature[Zone(zone)] = temp
        return f"the temperature in {zone} has been set to {temp} degree"
