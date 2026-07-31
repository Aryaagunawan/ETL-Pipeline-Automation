import logging
from utils.load import load
from utils.extract import extract
from utils.transform import transform

# Konfigurasi logging agar lebih mudah menelusuri proses
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_pipeline():
    try:
        # Langkah 1: Ekstraksi data
        raw_data = extract()
        if raw_data.empty:
            return

        # Langkah 2: Transformasi data
        cleaned_data = transform(raw_data)

        # Langkah 3: Load data ke berbagai tujuan
        load_results = load(
            df=cleaned_data,
            db_url="postgresql://developer:098765@localhost:5432/dbfashion",
            csv_file_path="products.csv",
            spreadsheet_id="1fW_Q9BmyL0Y31gWIzM_VGsaE2gKrLrJMPABle9Tu3Tc"
        )

        # Menampilkan ringkasan hasil
        total_tasks = len(load_results)
        successful = sum(load_results.values())
        success_percentage = (successful / total_tasks) * 100

        print("\n=== Ringkasan Proses ===")
        print(f"Total tugas       : {total_tasks}")
        print(f"Berhasil          : {successful}")
        print(f"Gagal             : {total_tasks - successful}")
        print(f"Tingkat Keberhasilan : {success_percentage:.1f}%")

        logging.info(f"Hasil pemuatan: {load_results}")

    except Exception as err:
        logging.error(f"Terjadi kesalahan saat menjalankan pipeline: {err}")

if __name__ == "__main__":
    run_pipeline()
