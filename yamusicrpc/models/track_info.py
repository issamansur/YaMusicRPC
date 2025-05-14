class TrackInfo:
    title: str
    artists: str
    duration: int
    progress: int

    def __init__(self, title: str, artist: str, duration: int, progress: int) -> None:
        self.title = title
        self.artists = artist
        self.duration = duration
        self.progress = progress
