# Story scenes: one short dialogue per city, built on the grammar and words of that leg's three units.
# Each line: (what the other person says, [(reply, kind, feedback in Uzbek), ...]).
# kind 1 = the best reply, 0 = a grammar mistake from this leg, 2 = correct English but it does not fit the talk.
# The learner may try again after a wrong reply; only the first choice counts for the stars.
# Story: Emma from London visits Uzbekistan (legs 1-5), then the learner travels the world (legs 6-14).

SCENES = [
{"title": "Welcome to Tashkent", "who": "Emma", "intro": "Emma Londondan keldi. Siz uni Toshkent aeroportida kutib oldingiz.",
 "lines": [
  ("Hi! I'm Emma. Nice to meet you!", [
    ("Nice to meet you too! Welcome to Tashkent.", 1, "Zo'r! Tabiiy va xushmuomala javob."),
    ("Nice to meet you too! You is welcome here.", 0, "'You is' xato: 'you' bilan 'are' ishlatiladi."),
    ("I'm fifteen kilometres from here.", 2, "Gap to'g'ri, lekin tanishuvga mos javob emas.")]),
  ("Is there a café near here? I'm hungry.", [
    ("Yes, there's a nice café next to the metro station.", 1, "To'g'ri: birlik ot bilan 'there is'."),
    ("Yes, there are a nice café next to the metro station.", 0, "'a café' birlik, shuning uchun 'there is' kerak."),
    ("Yes, I'm hungry too. Goodbye!", 2, "Emma joy so'rayapti, suhbatni to'xtatib qo'ymang.")]),
  ("Who is that man? He's waving at us.", [
    ("That's my uncle. He's waiting for us in the car.", 1, "Ayni paytdagi harakat: 'He's waiting'. Barakalla!"),
    ("That's my uncle. He wait for us in the car.", 0, "Hozir bo'layotgan harakat: 'He is waiting' (present continuous)."),
    ("That's my uncle's car. It's white.", 2, "Emma odam haqida so'radi, mashina haqida emas.")]),
  ("Does your family live in the city centre?", [
    ("No, we live in Chilanzar. My parents both work in the centre.", 1, "Ajoyib: 'we live', 'my parents work'."),
    ("No, we lives in Chilanzar. My parents works in the centre.", 0, "Ko'plikda fe'lga -s qo'shilmaydi: 'we live', 'they work'."),
    ("No, they don't like green tea.", 2, "Savol yashash joyi haqida edi.")]),
  ("What do you usually do at the weekend?", [
    ("I usually play football with my friends and help my mum.", 1, "Odat uchun present simple: 'I usually play'."),
    ("I am usually playing football with my friends.", 0, "Odat haqida present simple ishlatiladi: 'I usually play'."),
    ("The weekend is Saturday and Sunday.", 2, "To'g'ri gap, lekin Emma sizning odatingizni so'radi.")])],
 "finale": "Tell Emma about your family: who they are and what they do every day."},

{"title": "A day in Samarkand", "who": "Emma", "intro": "Emma bilan Samarqanddasiz. U kecha Registonni ko'rdi.",
 "lines": [
  ("I visited the Registan yesterday. Did you go there last year?", [
    ("Yes, I did. I went there with my class last spring.", 1, "To'g'ri: 'go' ning o'tgan zamoni 'went'."),
    ("Yes, I did. I goed there with my class.", 0, "'go' noto'g'ri fe'l, o'tgan zamoni 'went'."),
    ("Yes, I go to school by bus.", 2, "Emma o'tgan yil haqida so'radi, siz odatingizni aytdingiz.")]),
  ("What did you do last weekend?", [
    ("I went camping with my cousins. It was great!", 1, "Zo'r: o'tgan zamon to'g'ri ishlatildi."),
    ("I did went camping with my cousins.", 0, "Darak gapda 'did' kerak emas: 'I went camping'."),
    ("I'm going to go camping next weekend.", 2, "Savol o'tgan dam olish kunlari haqida edi.")]),
  ("Were you tired after the trip?", [
    ("Yes, I was very tired, but I was happy.", 1, "To'g'ri: 'I was'."),
    ("Yes, I were very tired.", 0, "'I' bilan 'was' ishlatiladi."),
    ("Yes, the trip is on Monday.", 2, "Vaqt mos emas: u o'tgan safar haqida so'radi.")]),
  ("Do you have any hobbies?", [
    ("Yes, I'm interested in photography. I took a lot of photos here.", 1, "Ajoyib: 'interested in' + o'tgan zamon."),
    ("Yes, I'm interesting in photography.", 0, "O'zingiz qiziqsangiz 'interested in'; 'interesting' esa biror narsa qiziq bo'lsa."),
    ("Yes, my hobby starts at 9 o'clock.", 2, "Sevimli mashg'ulot soat bilan boshlanmaydi.")]),
  ("When did Samarkand become so famous?", [
    ("It became famous a long time ago, on the Silk Road.", 1, "To'g'ri: 'become' → 'became'."),
    ("It becomed famous a long time ago.", 0, "'become' noto'g'ri fe'l: 'became'."),
    ("It becomes famous tomorrow.", 2, "Vaqt mos emas.")])],
 "finale": "Tell Emma about your best weekend: where you went and what you did."},

{"title": "The match in Bukhara", "who": "Emma", "intro": "Buxoroda Emma bilan futbol ko'ryapsiz. Keyin u Arkka yo'l so'raydi.",
 "lines": [
  ("Sorry I'm late! What were you doing when I called?", [
    ("I was watching the match on TV.", 1, "To'g'ri: past continuous 'I was watching'."),
    ("I watching the match on TV.", 0, "'was' tushib qoldi: 'I was watching'."),
    ("I watch the match every day.", 2, "U aynan o'sha paytda nima qilayotganingizni so'radi.")]),
  ("Look! Who scored that goal?", [
    ("Our best player scored it. The fans are going crazy!", 1, "Zo'r: 'scored' (o'tgan zamon)."),
    ("Our best player score it.", 0, "O'tgan harakat: 'scored'."),
    ("The referee has a whistle.", 2, "U kim gol urganini so'radi.")]),
  ("Do you enjoy playing football?", [
    ("Yes, I love playing. I want to join a club.", 1, "To'g'ri: 'love playing', 'want to join'."),
    ("Yes, I enjoy to play. I want joining a club.", 0, "'enjoy' dan keyin -ing, 'want' dan keyin 'to + fe'l'."),
    ("Yes, I enjoy tea with sugar.", 2, "Savol futbol haqida edi.")]),
  ("How do I get to the Ark from here?", [
    ("Go straight on and turn left at the pool. Don't cross the big road.", 1, "Ajoyib: yo'l ko'rsatishda buyruq mayli."),
    ("Going straight on and to turn left at the pool.", 0, "Yo'l ko'rsatishda buyruq ishlatiladi: 'Go straight on... turn left'."),
    ("I went to the Ark last year.", 2, "U yo'l so'radi, siz tajribangizni aytdingiz.")]),
  ("I saw a stork on the minaret! What was it doing?", [
    ("It was building a nest. Storks love Bukhara!", 1, "To'g'ri: 'It was building'. Laylak xursand!"),
    ("It were building a nest.", 0, "'It' bilan 'was' ishlatiladi."),
    ("It is a bird that likes football.", 2, "Qiziq, lekin savolga javob emas.")])],
 "finale": "Describe a match you watched: what were people doing when something exciting happened?"},

{"title": "School talk in Khiva", "who": "Emma", "intro": "Xivada, Ichan Qal'ada. Emma bilan maktab va sayohatlar haqida gaplashyapsiz.",
 "lines": [
  ("Have you ever been to Khiva before?", [
    ("Yes, I have. I've been here twice with my class.", 1, "To'g'ri: 'Yes, I have' + 'I've been'."),
    ("Yes, I have. I've went here twice.", 0, "Present perfect: 'have been'; 'have went' bo'lmaydi."),
    ("Yes, I am. I am in Khiva.", 2, "'Have you ever...?' savoliga 'Yes, I have' deb javob beriladi.")]),
  ("How long have you studied English?", [
    ("I've studied English for five years, since I was nine.", 1, "Ajoyib: 'for five years', 'since I was nine'."),
    ("I've studied English since five years.", 0, "Muddat uchun 'for'; 'since' boshlanish nuqtasi bilan keladi."),
    ("English is a language.", 2, "Savol qancha vaqtdan beri o'rganayotganingiz haqida.")]),
  ("What's your favourite subject?", [
    ("My favourite subject is history. We have it three times a week.", 1, "To'g'ri: 'subject is'."),
    ("My favourite subject are history.", 0, "'subject' birlik: 'is'."),
    ("My favourite subject is Tuesday.", 2, "Seshanba fan emas!")]),
  ("Have you finished your exams yet?", [
    ("Not yet. I haven't taken my English exam yet.", 1, "Zo'r: 'yet' bilan present perfect."),
    ("Not yet. I didn't took my English exam.", 0, "'yet' bilan: 'I haven't taken'. 'didn't took' ham xato."),
    ("Yes, the exam was very tall.", 2, "Imtihon baland bo'lmaydi.")]),
  ("This city is amazing! I've just bought a souvenir.", [
    ("Great! What have you bought?", 1, "To'g'ri savol: 'What have you bought?'"),
    ("Great! What did you have bought?", 0, "To'g'ri shakl: 'What have you bought?'"),
    ("Great! My school starts at eight.", 2, "Suhbat mavzusidan chetga chiqdingiz.")])],
 "finale": "Tell Emma about your school: your subjects, your teachers, and something you have never done but want to do."},

{"title": "Silk in Fergana", "who": "Emma", "intro": "Marg'ilondagi ipak fabrikasidasiz. Emma kelajak rejalaringiz haqida so'raydi.",
 "lines": [
  ("What are you going to do after school?", [
    ("I'm going to study medicine. I want to be a doctor.", 1, "To'g'ri: 'I'm going to study'."),
    ("I going to study medicine.", 0, "'am' tushib qoldi: 'I am going to'."),
    ("I'm going to school now.", 2, "U maktabdan keyingi reja haqida so'radi.")]),
  ("Whose scarf is this? It's beautiful.", [
    ("It's mine. My grandmother made it for me.", 1, "Ajoyib: 'mine', 'for me'."),
    ("It's my. My grandmother made it for I.", 0, "To'g'ri: 'It's mine', 'for me'."),
    ("It's a factory.", 2, "Ro'mol fabrika emas.")]),
  ("Do people work here full-time?", [
    ("Yes, most workers work full-time, but some students work part-time.", 1, "To'g'ri va aniq javob."),
    ("Yes, most worker works full-time.", 0, "Ko'plik: 'most workers work'."),
    ("Yes, silk is very soft.", 2, "Savol ish vaqti haqida edi.")]),
  ("It's very hot. I'm thirsty.", [
    ("I'll get you some water. Wait here.", 1, "Zo'r: darhol qabul qilingan qaror uchun 'I'll'."),
    ("I'm going to getting you some water.", 0, "Shu zahoti qaror: 'I'll get...'; 'going to getting' xato."),
    ("I'll be a teacher in ten years.", 2, "Emma chanqagan, suv kerak.")]),
  ("Do you think you'll visit London one day?", [
    ("I hope I will! Maybe I'll visit you next year.", 1, "To'g'ri: 'I'll visit'."),
    ("I hope I will! Maybe I will visiting you.", 0, "'will' dan keyin fe'lning asosiy shakli: 'will visit'."),
    ("I hope so. London is a bank.", 2, "London bank emas, shahar.")])],
 "finale": "Talk about your future: what job you are going to have and what you will do next summer."},

{"title": "Shopping in Istanbul", "who": "Seller", "intro": "Endi o'zingiz sayohatdasiz! Istanbuldagi Katta bozorda sotuvchi bilan gaplashyapsiz.",
 "lines": [
  ("Hello! Can I help you?", [
    ("Yes, please. How much does this lamp cost?", 1, "To'g'ri: 'does ... cost'."),
    ("Yes, please. How much does this lamp costs?", 0, "'does' dan keyin fe'lga -s qo'shilmaydi: 'cost'."),
    ("Yes, I can swim.", 2, "Sotuvchi yordam taklif qildi, suzish haqida so'ramadi.")]),
  ("It's 500 lira. It's a very good lamp.", [
    ("That's expensive. Could you give me a discount?", 1, "Zo'r: 'could' + fe'l. Savdolashish boshlandi!"),
    ("That's expensive. Could you to give me a discount?", 0, "'could' dan keyin 'to' qo'yilmaydi."),
    ("That's expensive. I must go to bed.", 2, "Savdolashish o'rniga suhbatni to'xtatdingiz.")]),
  ("OK, 400 lira. Cash or card?", [
    ("By card, please. Here you are.", 1, "To'g'ri: 'by card' / 'in cash'."),
    ("In card, please.", 0, "'by card' deyiladi."),
    ("Cards are made of plastic.", 2, "Gap to'g'ri, lekin savolga javob emas.")]),
  ("When do you fly home?", [
    ("My flight leaves on Friday at 7 am.", 1, "Ajoyib: jadval uchun present simple 'leaves'."),
    ("My flight is leave on Friday.", 0, "Jadval bo'yicha kelajak: 'My flight leaves...'."),
    ("I flew home last year.", 2, "Savol kelajak haqida edi.")]),
  ("You should visit the Blue Mosque before you go.", [
    ("Thanks! I'm meeting my friend there tomorrow.", 1, "To'g'ri: kelishilgan uchrashuv uchun 'I'm meeting'."),
    ("Thanks! I meeting my friend there tomorrow.", 0, "'am' tushib qoldi: 'I'm meeting'."),
    ("Thanks! You mustn't breathe.", 2, "Bu juda g'alati maslahat bo'lardi!")])],
 "finale": "Role-play a shop: ask for something, ask the price and try to get a lower price."},

{"title": "A guide in Rome", "who": "Guide", "intro": "Rimda gid bilan Kolizeydasiz. Keyin to'y an'analari haqida gaplashasiz.",
 "lines": [
  ("The Colosseum is almost 2,000 years old.", [
    ("Wow! When was it built?", 1, "To'g'ri: majhul nisbat 'When was it built?'"),
    ("Wow! When did it built?", 0, "Majhul nisbat: 'When was it built?'"),
    ("Wow! When is your birthday?", 2, "Qiziq savol, lekin mavzudan chetda.")]),
  ("It was finished in the year 80. Do you have old buildings in Uzbekistan?", [
    ("Yes, we do. The madrasas of the Registan were built hundreds of years ago.", 1, "Ajoyib: 'were built'."),
    ("Yes, we do. The madrasas of the Registan were build long ago.", 0, "Uchinchi shakl kerak: 'were built'."),
    ("Yes, we have a new phone.", 2, "Savol eski binolar haqida edi.")]),
  ("Would you like a guidebook?", [
    ("Yes, please. Is there an English one?", 1, "To'g'ri: unli tovush oldidan 'an'."),
    ("Yes, please. Is there a English one?", 0, "'English' unli bilan boshlanadi: 'an English one'."),
    ("Yes, please. My bag is heavy.", 2, "Suhbatni davom ettiradigan javob bering.")]),
  ("In Italy, the bride and groom throw sweets to the guests. What happens at Uzbek weddings?", [
    ("The guests are invited to a big party, and plov is served to everyone.", 1, "Zo'r: 'are invited', 'is served'."),
    ("The guests invited to a big party, and plov serves to everyone.", 0, "Majhul nisbat kerak: 'are invited', 'is served'."),
    ("Sweets are bad for your teeth.", 2, "To'g'ri, lekin savol to'y an'anasi haqida.")]),
  ("The Vatican is in Rome. Have you heard of it?", [
    ("Yes, the Vatican is the smallest country in the world.", 1, "To'g'ri: 'the smallest'."),
    ("Yes, Vatican is a smallest country in the world.", 0, "Orttirma daraja bilan 'the': 'the smallest'."),
    ("Yes, I heard a noise.", 2, "U Vatikan haqida so'radi.")])],
 "finale": "Describe a tradition from Uzbekistan: when it is celebrated and what is done. Use the passive (is made, is given)."},

{"title": "Café and shop in Paris", "who": "Waiter", "intro": "Parijda: avval kafeda buyurtma berasiz, keyin kiyim do'koniga kirasiz.",
 "lines": [
  ("Good morning! What would you like?", [
    ("Two croissants and some orange juice, please.", 1, "To'g'ri: 'two croissants', 'some juice'."),
    ("Two croissant and a milk, please.", 0, "Ko'plik 'croissants'; 'milk' sanalmaydi: 'some milk'."),
    ("I'd like a size medium.", 2, "Bu kafe, kiyim do'koni emas.")]),
  ("Would you like sugar in your coffee?", [
    ("Just a little, please.", 1, "To'g'ri: sanalmaydigan ot bilan 'a little'."),
    ("Just a few, please.", 0, "'sugar' sanalmaydi: 'a little'."),
    ("Just a jacket, please.", 2, "Kofega kurtka solinmaydi!")]),
  ("[Do'konda] Hello! Can I help you?", [
    ("Yes, can I try on these jeans?", 1, "Zo'r: 'jeans' ko'plik, 'these jeans'."),
    ("Yes, can I try on this jeans?", 0, "'jeans' faqat ko'plikda: 'these jeans'."),
    ("Yes, is it Monday today?", 2, "Do'kondagi suhbatga mos emas.")]),
  ("How do they fit?", [
    ("They're a bit tight. Do you have a bigger size?", 1, "To'g'ri: 'They're' (jeans ko'plik)."),
    ("It's a bit tight. Do you have a bigger size?", 0, "'jeans' ko'plik: 'They're'."),
    ("They're blue and French.", 2, "Savol o'lcham haqida edi.")]),
  ("How much money do you want to spend?", [
    ("Not much. I don't have many euros left.", 1, "Ajoyib: 'money' → much, 'euros' → many."),
    ("Not many. I don't have much euros left.", 0, "'money' sanalmaydi (much), 'euros' sanaladi (many)."),
    ("About three shoes.", 2, "Pul haqida so'radi.")])],
 "finale": "Order food in a café and buy clothes in a shop. Use some, any, much, many, a few, a little."},

{"title": "Emma's London", "who": "Emma", "intro": "Londonda Emma sizni kutib oldi! Endi u sizga shaharni ko'rsatyapti.",
 "lines": [
  ("Welcome to London! Is it colder than Tashkent?", [
    ("Yes, it's much colder and rainier than Tashkent!", 1, "To'g'ri: 'colder', 'rainier'."),
    ("Yes, it's more cold and more rainy.", 0, "Qisqa sifatlar -er oladi: 'colder', 'rainier'."),
    ("Yes, it's the capital.", 2, "U ob-havoni solishtirishni so'radi.")]),
  ("What's the most beautiful building in Tashkent?", [
    ("I think the Amir Timur Museum is the most beautiful.", 1, "Zo'r: uzun sifat bilan 'the most beautiful'."),
    ("I think the Amir Timur Museum is the beautifulest.", 0, "Uzun sifat: 'the most beautiful'."),
    ("I think buildings are made of stone.", 2, "Savol eng chiroyli bino haqida.")]),
  ("Let's go to the British Museum. Is it far from our hotel?", [
    ("No, it isn't. It's the nearest museum to our hotel.", 1, "To'g'ri: 'the nearest'."),
    ("No, it isn't. It's the most near museum.", 0, "'near' → 'the nearest'."),
    ("No, it's a museum.", 2, "U masofa haqida so'radi.")]),
  ("London buses are big and red. What are buses like in Tashkent?", [
    ("They're not as big as London buses, but they're newer.", 1, "Ajoyib: 'as big as', 'newer'."),
    ("They're not as bigger as London buses.", 0, "'as ... as' orasida oddiy sifat: 'as big as'."),
    ("They're my favourite colour.", 2, "Javob savolga mos emas.")]),
  ("What was the best day of your trip so far?", [
    ("Today! It was better than all the other days.", 1, "To'g'ri: good → better → the best."),
    ("Today! It was more good than the other days.", 0, "'good' → 'better'."),
    ("Tomorrow is Saturday.", 2, "U eng yaxshi kun haqida so'radi.")])],
 "finale": "Compare your town with London: which is bigger, older, more expensive? What is the best place in your town?"},

{"title": "Arriving in New York", "who": "Officer", "intro": "Nyu-York aeroportidasiz: avval pasport nazorati, keyin yo'l topasiz.",
 "lines": [
  ("Good evening. May I see your passport, please?", [
    ("Of course. Here you are.", 1, "To'g'ri: tayyor ibora 'Here you are'."),
    ("Of course. Here you is.", 0, "Ibora: 'Here you are'."),
    ("Of course. I like passports.", 2, "Pasportni berishingiz kerak edi.")]),
  ("How long are you staying in the USA?", [
    ("For two weeks. I'm leaving on the 20th of June.", 1, "Zo'r: 'for two weeks', 'on the 20th'."),
    ("During two weeks. I'm leaving in the 20th of June.", 0, "Muddat: 'for two weeks'; sana: 'on the 20th'."),
    ("I'm staying at the window.", 2, "U qancha vaqt qolishingizni so'radi.")]),
  ("[Ko'chada] You look lost. Can I help?", [
    ("Yes, please. How do I get to Central Park?", 1, "To'g'ri savol tartibi: 'How do I get...?'"),
    ("Yes, please. How I get to Central Park?", 0, "Savolda 'do' kerak: 'How do I get...?'"),
    ("Yes, I lost my weight.", 2, "U yo'lni so'rayapti.")]),
  ("Take the subway. Get off at 59th Street and walk across the road.", [
    ("Thanks! You explained that very clearly.", 1, "To'g'ri: fe'l bilan ravish 'clearly'."),
    ("Thanks! You explained that very clear.", 0, "Fe'lni ravish tasvirlaydi: 'clearly'."),
    ("Thanks! The subway is under the sea.", 2, "Metro dengiz ostida emas.")]),
  ("Enjoy your trip! Be careful, the streets are busy.", [
    ("Thanks, I will. I'll cross the road carefully!", 1, "Ajoyib: 'carefully'."),
    ("Thanks, I will. I'll cross the road careful!", 0, "Ravish kerak: 'carefully'."),
    ("Thanks, I missed my flight yesterday.", 2, "Suhbatga mos xayrlashuv emas.")])],
 "finale": "Explain the way from your school to your home: use go along, turn left, across, next to, opposite."},

{"title": "At a pharmacy in Rio", "who": "Pharmacist", "intro": "Rio-de-Janeyroda quyosh juda kuchli. Dorixonaga kirdingiz.",
 "lines": [
  ("Hello. What's the matter?", [
    ("I've got a headache and a sore throat.", 1, "To'g'ri: 'a headache', 'a sore throat'."),
    ("I've got a headache and a throat sore.", 0, "To'g'ri tartib: 'a sore throat'."),
    ("I've got a new passport.", 2, "Dorixonachi sog'lig'ingizni so'radi.")]),
  ("Have you got a temperature?", [
    ("I don't think so, but I feel very tired.", 1, "Zo'r: o'zingiz haqingizda 'tired'."),
    ("I don't think so, but I feel very tiring.", 0, "O'zingiz charchagan bo'lsangiz: 'tired'."),
    ("Yes, 30 degrees is nice for the beach.", 2, "U tana haroratini so'radi, ob-havoni emas.")]),
  ("If you take this medicine, you'll feel better tomorrow.", [
    ("Thank you. What will happen if I forget to take it?", 1, "To'g'ri: 'if I forget' ('if' qismida 'will' yo'q)."),
    ("Thank you. What will happen if I will forget it?", 0, "'if' dan keyin 'will' ishlatilmaydi: 'if I forget'."),
    ("Thank you. Medicine is a school subject.", 2, "Suhbatga mos emas.")]),
  ("If I were you, I would drink more water and stay out of the sun.", [
    ("That's good advice. If I had a hat, I would wear it now.", 1, "Ajoyib: ikkinchi shart 'If I had..., I would...'."),
    ("That's good advice. If I would have a hat, I'd wear it.", 0, "Ikkinchi shart: 'If I had a hat, I would wear it'."),
    ("That's good advice. Water is blue.", 2, "Maslahatga mos javob emas.")]),
  ("What would you do if you had a free day here?", [
    ("If I had a free day, I would go to Sugarloaf Mountain.", 1, "To'g'ri: 'If I had..., I would...'."),
    ("If I have a free day, I would go to Sugarloaf Mountain.", 0, "Xayoliy vaziyat: 'If I had..., I would...'."),
    ("Yesterday I had a free day.", 2, "Savol xayoliy vaziyat haqida edi.")])],
 "finale": "What would you do if you won a trip anywhere in the world? And what will you do if it rains this weekend?"},

{"title": "The pyramids of Cairo", "who": "Omar", "intro": "Qohirada, piramidalar yonida. Misrlik do'stingiz Omar bilan gaplashyapsiz.",
 "lines": [
  ("It's so hot today, isn't it?", [
    ("Yes, it is! It's such a hot day.", 1, "To'g'ri: sifat + ot oldida 'such a'."),
    ("Yes, it is! It's so a hot day.", 0, "Sifat + ot bilan: 'such a hot day'."),
    ("Yes, it is! My phone is new.", 2, "Mavzudan chetga chiqdingiz.")]),
  ("I don't like very hot weather.", [
    ("Neither do I. Let's find some shade.", 1, "Zo'r: inkor gapga qo'shilish 'Neither do I'."),
    ("So do I. Let's find some shade.", 0, "Inkor gapga 'Neither do I' bilan qo'shilamiz."),
    ("Neither do I. Let's stand in the sun.", 2, "O'zingizga zid javob!")]),
  ("You've got a camera, haven't you?", [
    ("No, I haven't, but I can take photos with my phone.", 1, "To'g'ri: 'haven't you?' ga 'No, I haven't'."),
    ("No, I don't have, but I can take photos with my phone.", 0, "Javob: 'No, I haven't'."),
    ("No, the pyramids are old.", 2, "Savol kamera haqida edi.")]),
  ("Oh no, my phone's battery is dead!", [
    ("Don't worry. You can use my charger.", 1, "Ajoyib yordam: 'can use'."),
    ("Don't worry. You can uses my charger.", 0, "'can' dan keyin -s qo'shilmaydi."),
    ("Don't worry. The website is new.", 2, "Bu muammoni hal qilmaydi.")]),
  ("The pyramids are amazing, aren't they?", [
    ("They are! I'll post a photo online tonight.", 1, "To'g'ri: 'post a photo online'."),
    ("They are! I'll post a photo in online tonight.", 0, "'online' dan oldin 'in' kerak emas."),
    ("They aren't. They're amazing.", 2, "O'zingizga zid javob.")])],
 "finale": "Talk about the technology you use every day. Use question tags: You use Telegram, don't you?"},

{"title": "Mount Fuji trip", "who": "Yuki", "intro": "Tokioda yapon do'stingiz Yuki bilan Fudzi tog'iga boryapsiz.",
 "lines": [
  ("Who is the man in this photo?", [
    ("He's the teacher who taught me Japanese words online.", 1, "To'g'ri: odamlar uchun 'who'."),
    ("He's the teacher which taught me Japanese words online.", 0, "Odamlar uchun 'who' ishlatiladi."),
    ("He's a mountain which is very high.", 2, "Suratdagi odam tog' emas!")]),
  ("Did you see Mount Fuji from the train?", [
    ("No, because clouds had covered it before we arrived.", 1, "Zo'r: oldinroq bo'lgan harakat 'had covered'."),
    ("No, because clouds have covered it before we arrived.", 0, "O'tmishdagi boshqa harakatdan oldin: 'had covered'."),
    ("No, because Fuji is in Japan.", 2, "Bu sabab bo'la olmaydi.")]),
  ("What's the weather like in Uzbekistan in summer?", [
    ("It's very hot and sunny. It can be 40 degrees!", 1, "To'g'ri: 'sunny' (sifat)."),
    ("It's very hot and sun.", 0, "Sifat kerak: 'sunny'."),
    ("It's a country which has a flag.", 2, "Savol ob-havo haqida edi.")]),
  ("This is the park where people watch the cherry blossoms.", [
    ("It's beautiful! Is this the place where the festival happens?", 1, "Ajoyib: joy uchun 'where'."),
    ("It's beautiful! Is this the place which the festival happens?", 0, "Joy haqida 'where' ishlatiladi."),
    ("It's beautiful! My phone has a camera.", 2, "Suhbatga mos davom emas.")]),
  ("Had you ever eaten sushi before you came to Japan?", [
    ("No, I hadn't. Today was my first time!", 1, "To'g'ri: 'Had you...?' ga 'No, I hadn't'."),
    ("No, I didn't had.", 0, "Javob: 'No, I hadn't'."),
    ("No, I'm eating now.", 2, "U Yaponiyaga kelishdan oldingi tajriba haqida so'radi.")])],
 "finale": "Describe a place in nature you love: what it looks like and what had happened before you first visited it."},

{"title": "Youth forum in Sydney", "who": "Journalist", "intro": "Sidneydagi xalqaro yoshlar ekologiya forumidasiz. Jurnalist sizdan intervyu olyapti.",
 "lines": [
  ("What is the biggest environmental problem in your country?", [
    ("I think it's water. The Aral Sea has lost most of its water.", 1, "To'g'ri: 'has lost'."),
    ("I think it's water. The Aral Sea has lose most of its water.", 0, "Present perfect: 'has lost'."),
    ("I think the biggest problem is my homework.", 2, "Forum global muammolar haqida.")]),
  ("What are young people doing to help?", [
    ("We're planting trees and recycling plastic at school.", 1, "Zo'r: 'We're planting... recycling...'."),
    ("We plant trees now and recycling plastic.", 0, "Hozirgi davomiy: 'We're planting and recycling'."),
    ("We're going to the cinema.", 2, "Savol atrof-muhitga yordam haqida.")]),
  ("The minister said, 'We will stop pollution.' Can you report it?", [
    ("The minister said that they would stop pollution.", 1, "To'g'ri: 'will' → 'would' + asosiy fe'l."),
    ("The minister said that they will stopped pollution.", 0, "Ko'chirma gapda 'would stop' bo'ladi."),
    ("The minister told pollution.", 2, "Ma'no chiqmadi.")]),
  ("How did you get interested in the environment?", [
    ("When I was twelve, I watched a film about plastic in the ocean.", 1, "Ajoyib: o'tgan zamon hikoyasi."),
    ("When I am twelve, I watched a film about plastic.", 0, "O'tmish: 'When I was twelve'."),
    ("When I was twelve, I was twelve.", 2, "Hech narsa aytmadingiz!")]),
  ("What will you do when you go home?", [
    ("I'm going to start a recycling club at my school.", 1, "To'g'ri: 'going to start'. Sayohat yakunlandi!"),
    ("I'm going to starting a recycling club.", 0, "'going to' + asosiy fe'l: 'going to start'."),
    ("I went home last year.", 2, "Savol kelajak haqida edi.")])],
 "finale": "Give a 45-second speech: one global problem, why it matters, and what you are going to do about it."},
]
