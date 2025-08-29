import tkinter as tk
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
import pandas as pd

# Müzik verisini oku
data = pd.read_csv('genres_v2.csv')

# Veri setini temizle: gerekli sütunları seç
data_cleaned = data[['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'valence', 'tempo']]

# Veriyi normalleştir
scaler = MinMaxScaler()
data_scaled = scaler.fit_transform(data_cleaned)

# KNN Modelini oluştur
model = NearestNeighbors(n_neighbors=10, metric='cosine')
model.fit(data_scaled)

# Şarkı ID'leri ile isimleri eşleştiren bir sözlük oluştur
song_id_name_dict = dict(zip(data['id'], data['song_name']))

# Kullanıcı playlisti
playlist = []

def get_custom_suggestions(query, suggestion_list):
    """Öneri listesinden kullanıcıya uygun müzikleri getir."""
    suggestions_set = {str(item) for item in suggestion_list if query.lower() in str(item).lower()}
    suggestions = list(suggestions_set)
    return suggestions

def get_song_id(song_name):
    """Şarkının ID'sini al"""
    result = data[data['song_name'] == song_name]
    if not result.empty:
        return result.iloc[0]['id']
    return None

def on_entry_change(*args):
    """Giriş kutusu her değiştiğinde önerileri güncelle"""
    user_input = entry.get()
    if not user_input:
        suggestion_listbox.delete(0, tk.END)
        return
    suggestions = get_custom_suggestions(user_input, custom_suggestion_list)
    suggestion_listbox.delete(0, tk.END)
    for suggestion in suggestions:
        suggestion_listbox.insert(tk.END, suggestion)

def add_to_playlist():
    """Seçilen şarkıyı playlist'e ekle"""
    selected_index = suggestion_listbox.curselection()
    if selected_index:
        selected_song = suggestion_listbox.get(selected_index)
        song_id = get_song_id(selected_song)
        if song_id:
            playlist.append(song_id)
            print(f"Playlist: {playlist}")

def get_user_playlist_features(playlist_ids):
    """Kullanıcının playlist'inde bulunan şarkıların özelliklerini al"""
    user_features = data[data['id'].isin(playlist_ids)][['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'valence', 'tempo']]
    return scaler.transform(user_features)

def recommend_songs(user_playlist):
    """Kullanıcının playlist'ine göre önerilen şarkıları getir"""
    user_features_scaled = get_user_playlist_features(user_playlist)
    distances, indices = model.kneighbors(user_features_scaled)
    
    recommended_songs = []
    for idx_list in indices:
        recommended_songs.extend(data.iloc[idx_list]['song_name'].values)
    
    return list(set(recommended_songs))  # Duplicates eliminasyonu

def show_recommendations():
    """Önerilen şarkıları göster"""
    recommendations = recommend_songs(playlist)
    
    # Yeni pencereyi oluştur
    recommend_window = tk.Toplevel(app)
    recommend_window.title("Önerilen Müzikler")

    # Listbox'u oluştur
    recommend_listbox = tk.Listbox(recommend_window, width=50, height=10)
    recommend_listbox.pack(padx=20, pady=20)

    # Önerilen müzikleri Listbox'a ekle
    for recommendation in recommendations:
        recommend_listbox.insert(tk.END, recommendation)

def clean_Playlist():
    """Playlist'i temizle"""
    global playlist
    playlist.clear()

# Tkinter UI hazırlığı
app = tk.Tk()
app.title("Müzik Öneri Uygulaması")
app.geometry("500x300")

# Giriş kutusu
entry = tk.Entry(app)
entry.place(x=170, y=15)
entry.bind("<KeyRelease>", on_entry_change)

# Şarkı öneri listbox'ı
suggestion_listbox = tk.Listbox(app, width=50, height=10)
suggestion_listbox.place(x=50, y=50)

# Playlist'e ekleme butonu
add_button = tk.Button(app, text="Playlist'e Ekle", command=add_to_playlist)
add_button.place(x=50, y=250)

# Öneri butonu
recommend_button = tk.Button(app, text="Önerileri Göster", command=show_recommendations)
recommend_button.place(x=177, y=250)

# Playlisti temizleme butonu
clean_button = tk.Button(app, text="Playlisti Temizle", command=clean_Playlist)
clean_button.place(x=315, y=250)

# Playlist listesi
playlist = []

# Öneri listesi
custom_suggestion_list = data['song_name']

# Tkinter uygulamasını başlat
app.mainloop()

