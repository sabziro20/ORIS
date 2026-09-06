class Playlist:
    def __init__(self):
        self.songs = list()

    def add_song(self, name, duration):
        self.songs.append((name, duration))
        print(f"Песня под названием {name} добавлена")

    def remove_song(self, name):
        if self.songs:
            for song in self.songs:
                if song[0].lower() == name.lower():
                    self.songs.remove(song)
                    print(f"Песня под названием {name} удалена")
                    return
            else:
                print("Песня не найдена")
        else:
            print("Ваш плейлист пустой")

    def total_duration(self):
        total = 0
        if self.songs:
            for song in self.songs:
                total += int(song[1])
        return total

    def __len__(self):
        return len(self.songs)

    def __str__(self):
        if not self.songs:
            return "Ваш плейлист пустой"
        res = "Список песен в плейлисте:\n"
        for song in self.songs:
            res += f"Название: {song[0]}, продолжительность {song[1]} секунд\n"
        return res


pl = Playlist()
pl.add_song("Поезда", 123)
pl.add_song("Ламба", 12)
pl.add_song("ЧЕЛОПУК", 412)
print(len(pl))
print(pl.total_duration())
pl.remove_song("Поезда")
print(pl.total_duration())
print(len(pl))
print(pl)

