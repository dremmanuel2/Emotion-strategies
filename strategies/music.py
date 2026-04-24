"""
音乐推荐策略 - 根据情绪推荐歌曲
"""
from typing import List, Dict
from loguru import logger
import asyncio

from models import UserInput, StrategyResponse, MethodResult, StateJudgment, EmotionType, MusicSuggestion
from strategies.base import BaseStrategy


class MusicOfferStrategy(BaseStrategy):
    """音乐推荐策略"""
    
    def __init__(self):
        super().__init__()
        self.name = "MUSIC_OFFER"
        self.description = "【音乐推荐】根据情绪状态推荐适合的老歌和纯音乐，通过音乐调节情绪（悲伤 - 温柔/焦虑 - 舒缓/愤怒 - 平和/积极 - 欢快）"
        self.suitable_emotions = ["sad", "anxious", "angry", "positive"]
        self.suitable_stages = ["venting", "neutral"]
        self.suitable_intensities = ["low", "medium"]
        self.suitable_risks = ["low"]
        self.methods_info = [
            {"name": "询问音乐偏好", "desc": "询问用户是否想听音乐，根据情绪调整询问方式"},
            {"name": "推荐歌曲", "desc": "根据情绪从歌曲库中选择 3 首适合的歌曲推荐，包含歌曲名称、艺术家和描述"}
        ]
        
        # 歌曲库 - 老年人熟悉的歌曲
        self.song_database = {
            EmotionType.SAD: [
                MusicSuggestion(
                    song_name="月亮代表我的心",
                    artist="邓丽君",
                    description="这首歌很温柔，听着心里会暖暖的",
                    emotion="sad"
                ),
                MusicSuggestion(
                    song_name="甜蜜蜜",
                    artist="邓丽君",
                    description="旋律很简单，让人想起很多美好的事情",
                    emotion="sad"
                ),
                MusicSuggestion(
                    song_name="但愿人长久",
                    artist="王菲",
                    description="歌词很有意境，适合安静的时候听",
                    emotion="sad"
                ),
            ],
            EmotionType.ANXIOUS: [
                MusicSuggestion(
                    song_name="平湖秋月",
                    artist="纯音乐",
                    description="平静的曲子，能让心慢慢静下来",
                    emotion="anxious"
                ),
                MusicSuggestion(
                    song_name="渔舟唱晚",
                    artist="纯音乐",
                    description="古筝曲，很舒缓，适合放松",
                    emotion="anxious"
                ),
                MusicSuggestion(
                    song_name="梅花三弄",
                    artist="纯音乐",
                    description="古典名曲，听着很安心",
                    emotion="anxious"
                ),
            ],
            EmotionType.ANGRY: [
                MusicSuggestion(
                    song_name="茉莉花",
                    artist="宋祖英",
                    description="柔和的民歌，能化解心里的烦躁",
                    emotion="angry"
                ),
                MusicSuggestion(
                    song_name="小城故事",
                    artist="邓丽君",
                    description = "温柔的歌声，让人心情平和",
                    emotion="angry"
                ),
                MusicSuggestion(
                    song_name="一剪梅",
                    artist="费玉清",
                    description="悠扬的旋律，能帮助平静下来",
                    emotion="angry"
                ),
            ],
            EmotionType.POSITIVE: [
                MusicSuggestion(
                    song_name="南泥湾",
                    artist="郭兰英",
                    description="欢快的老歌，让好心情更好",
                    emotion="positive"
                ),
                MusicSuggestion(
                    song_name="洪湖水浪打浪",
                    artist="王玉珍",
                    description="经典的欢快歌曲，很有活力",
                    emotion="positive"
                ),
                MusicSuggestion(
                    song_name="我的祖国",
                    artist="郭兰英",
                    description="大气磅礴，让人心情舒畅",
                    emotion="positive"
                ),
            ],
            EmotionType.NEUTRAL: [
                MusicSuggestion(
                    song_name="夜来香",
                    artist="邓丽君",
                    description="经典老歌，适合日常听",
                    emotion="neutral"
                ),
                MusicSuggestion(
                    song_name="何日君再来",
                    artist="周璇",
                    description="怀旧金曲，很有韵味",
                    emotion="neutral"
                ),
                MusicSuggestion(
                    song_name="天涯歌女",
                    artist="周璇",
                    description="老上海经典，听着很舒服",
                    emotion="neutral"
                ),
            ]
        }
    
    def can_handle(self, user_input: UserInput, state: StateJudgment) -> bool:
        """发泄中低密度或积极情绪使用此策略"""
        return (
            (user_input.emotion in [EmotionType.SAD, EmotionType.ANXIOUS, EmotionType.ANGRY] and
             state.stage.value == "venting" and
             state.intensity in ["low", "medium"]) or
            user_input.emotion == EmotionType.POSITIVE
        )
    
    async def execute(self, user_input: UserInput, state: StateJudgment) -> StrategyResponse:
        """执行音乐推荐策略"""
        logger.info(f"[{self.name}] 执行音乐推荐策略，情绪：{user_input.emotion}")
        
        methods: List[MethodResult] = []
        
        # 询问是否想听音乐
        ask_method = self._ask_music_preference(user_input)
        methods.append(ask_method)
        
        # 推荐歌曲
        recommend_method = self._recommend_songs(user_input.emotion)
        methods.append(recommend_method)
        
        # 生成回复
        response_text = self._generate_response(methods)
        
        return StrategyResponse(
            strategy=self.name,
            methods=methods,
            response_text=response_text,
            metadata={
                "emotion": user_input.emotion.value,
                "songs_count": len(self.song_database.get(user_input.emotion, []))
            }
        )
    
    def _ask_music_preference(self, user_input: UserInput) -> MethodResult:
        """询问音乐偏好"""
        if user_input.emotion in [EmotionType.SAD, EmotionType.ANXIOUS, EmotionType.ANGRY]:
            content = (
                "要不要听点舒缓的音乐？\n"
                "有时候音乐能让人放松一点。\n"
                "我这儿有几首比较温柔的老歌，你想听吗？"
            )
        else:  # POSITIVE
            content = (
                "心情这么好，要不要放点你喜欢的歌助助兴？\n"
                "想不想听点音乐？我可以根据你的喜好推荐几首。"
            )
        
        self._log_execution("询问音乐偏好")
        return self._create_method_result("询问音乐偏好", content)
    
    def _recommend_songs(self, emotion: EmotionType) -> MethodResult:
        """推荐歌曲"""
        songs = self.song_database.get(emotion, self.song_database[EmotionType.NEUTRAL])
        
        content = "我给你推荐几首适合现在听的歌吧：\n\n"
        for i, song in enumerate(songs[:3], 1):
            content += f"{i}. 《{song.song_name}》- {song.artist}\n"
            content += f"   {song.description}\n\n"
        
        content += "你想听哪一首？或者你有其他喜欢的歌也可以告诉我。"
        
        self._log_execution("推荐歌曲", f"情绪：{emotion.value}, 数量：{len(songs[:3])}")
        return self._create_method_result(
            "推荐歌曲",
            content,
            suggestions=[s.song_name for s in songs]
        )
    
    def get_songs_by_emotion(self, emotion: EmotionType) -> List[MusicSuggestion]:
        """根据情绪获取歌曲列表"""
        return self.song_database.get(emotion, [])
    
    def _generate_response(self, methods: List[MethodResult]) -> str:
        """生成回复"""
        parts = [m.content for m in methods]
        return "\n\n".join(parts)