# DISCID // Bahasa Indonesia

DISCID adalah bagian dari rangkaian program analisa kepribadian DISC dalam bahasa Indonesia yang dilakukan oleh tim AMIKOM-Profiling dari Universitas AMIKOM Yogyakarta.

Untuk dapat menggunakan program ini, diperlukan dependencies sebagai berikut :

Python3,

MongoDB,

Library pymongo, SON, json, requests, re, dan Regex,

InaNLP Rest API yang bisa didapatkan di https://github.com/panggi/pujangga,

Setelah selesai melakukan instalasi kebutuhan yang diperlukan, daftar kata kunci yang terdapat di dalam folder "keywords" dapat di-import ke dalam basis data MongoDB dengan nama AMIKOM-Profiling.

Jika sudah, pengguna dapat menjalankan program dengan menuliskan perintah

python3 -c "import pre"

melalui terminal di dalam folder DISCID yang telah di-download / dikloning dari repository ini.

# DISCID // English

DISCID is a part of DISC profiling analysis pipelines in Indonesian language contributed by AMIKOM-Profiling research team from University AMIKOM Yogyakarta.

To be able to run this pipeline, these dependencies are required :

Python3,

MongoDB,

Library pymongo, SON, json, requests, re, dan Regex,

InaNLP Rest API which is available on https://github.com/panggi/pujangga,

After the required dependencies are installed correctly, keyword lists which are available in the folder "keywords" might be imported to MongoDB database as AMIKOM-Profiling.

Users may then run the program by typing 

python3 -c "import pre"

via the commandline directly from DISCID folder which was downloaded / cloned from this repository.
