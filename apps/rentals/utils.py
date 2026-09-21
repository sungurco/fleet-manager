def turkish_upper(text):
    """Python'un varsayılan str.upper() metodu Türkçe'deki noktalı/noktasız
    I ayrımını doğru yapmaz (örn. "kirim" -> "KIRIM" yerine "KİRİM" bekleriz,
    "yılmaz" -> "YILMAZ" bekleriz ama "i" harfini yanlış çevirebilir). Bu
    yüzden özel harfleri elle eşleyip kalanına standart upper() uygularız.
    """
    if not text:
        return text
    return text.replace("i", "İ").replace("ı", "I").upper()
