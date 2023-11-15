import tkinter as tk
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import pandas as pd

def get_custom_suggestions(query, suggestion_list):
    # Set kullanarak tekrar eden şarkıları önle
    suggestions_set = {str(item) for item in suggestion_list if query.lower() in str(item).lower()}
    suggestions = list(suggestions_set)
    return suggestions

def get_song_id(song_name):
    data_ = pd.read_csv('genres_v2.csv')
    data_['id'] = range(1, len(data_) + 1)

    # Veri setinde şarkı ismini ara
    result = data_[data_['song_name'] == song_name]

    if not result.empty:
        song_id = result.iloc[0]['id']
        return song_id
    else:
        return None

def on_entry_change(*args):
    user_input = entry.get()

    # Girilen kelime yok ise alt kısmı temizle
    if not user_input:
        suggestion_listbox.delete(0, tk.END)
        return

    suggestions = get_custom_suggestions(user_input, custom_suggestion_list)

    # Eğer öneri yoksa, alt kısmı temizle
    if not suggestions:
        suggestion_listbox.delete(0, tk.END)
        return

    suggestion_listbox.delete(0, tk.END)
    for suggestion in suggestions:
        suggestion_listbox.insert(tk.END, suggestion)

def add_to_playlist():
    selected_index = suggestion_listbox.curselection()
    if selected_index:
        selected_song = suggestion_listbox.get(selected_index)
        song_id = get_song_id(selected_song)
        playlist.append(song_id)
        print("Playlist:", playlist)

def recommended_music(playlist):
    # Kullanıcının dinlediği her şarkının özelliklerini al
    user_song_features = data[data['id'].isin(playlist)]

    # Min-Max normalizasyonu uygula
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data)
    user_song_features_scaled = scaler.transform(user_song_features)

    # Cosine similarity hesapla
    similarities = cosine_similarity(user_song_features_scaled, data_scaled)

    # Benzerlik skorlarına göre önerileri sırala
    recommendations_indices = similarities.mean(axis=0).argsort()[::-1][:10]
    recommendations = data.iloc[recommendations_indices]
    recommended_song_names = [song_id_name_dict[id] for id in recommendations["id"]]

    return recommended_song_names

def clean_Playlist():
    global playlist
    playlist.clear()

def show_recommendations():
    global song_id_name_dict 

    recommendations = recommended_music(playlist + playlist)
    
    # Yeni pencereyi oluştur
    recommend_window = tk.Toplevel(app)
    recommend_window.title("Önerilen Müzikler")

    # Listbox'u oluştur
    recommend_listbox = tk.Listbox(recommend_window, width=50, height=10)
    recommend_listbox.pack(padx=20, pady=20)

    # Önerilen müzikleri Listbox'a ekle
    for recommendation in recommendations:
        recommend_listbox.insert(tk.END, recommendation)

# Öneri listesini tanımla
data = pd.read_csv('genres_v2.csv')
custom_suggestion_list = data['song_name']
# "id" sütununu sıralı bir şekilde güncelle
data['id'] = range(1, len(data) + 1)

# Veri setinizdeki "genre" sütununu seçin
genre_sutun = data['genre']

# Tüm farklı "genre" değerlerini sıralayın ve benzersiz tamsayılarla eşleyin
genre_listesi = genre_sutun.unique()
genre_dict = {genre: i for i, genre in enumerate(genre_listesi)}

# "genre" sütununu benzersiz tamsayılara dönüştürün ve yeni bir sütun ekleyin
data['genre_id'] = genre_sutun.map(genre_dict)

# Hangi değerin hangi tamsayıya karşılık geldiğini gösteren bir sözlük oluşturun
genre_sozluk = {genre: genre_id for genre, genre_id in genre_dict.items()}

# Şarkı ID'leri ile isimleri eşleştiren bir sözlük oluştur
song_id_name_dict = dict(zip(data['id'], data['song_name']))

# Gereksiz verileri stunlarını sil
data.drop(columns=['uri','track_href','analysis_url','Unnamed: 0','title','song_name','genre','type'],axis = 1,inplace = True)

# Veri setindeki tüm verileri aynı türe çevir
data = data.astype(float)

# Tkinter uygulamasını oluştur
app = tk.Tk()
app.title("Öneri Uygulaması")
app.geometry("500x300")

# Giriş kutusu oluştur
entry = tk.Entry(app)
entry.place(x = 170, y = 15)
entry.bind("<KeyRelease>", on_entry_change)

# Önerileri göstermek için Listbox widget'ini kullan
suggestion_listbox = tk.Listbox(app, width=50, height=10)
suggestion_listbox.place(x=50, y=50) 

# Ekleme butonu oluştur
add_button = tk.Button(app, text="Playlist'e Ekle", command=add_to_playlist)
add_button.place(x=50, y=250)  

# Öneri butonu oluştur
recommend_button = tk.Button(app, text="Önerileri Göster", command=show_recommendations)
recommend_button.place(x=177, y=250)  

# Playlisti temizleme butonu oluştur
clean_button = tk.Button(app, text="Playlisti Temizle", command=clean_Playlist)
clean_button.place(x=315, y=250)  

# Playlist listesini oluştur
playlist = []

# Tkinter uygulamasını başlat
app.mainloop()
