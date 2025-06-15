import streamlit as st
from supabase import create_client, Client

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ===== Ambil semua data dari tabel =====
def fetch_customer_data():
    response = supabase.table("customer_guidance_invoice").select("*").execute()
    data = response.data

    # Kalau datanya kosong
    if not data:
        return []

    # Ubah nama kolom agar cocok dengan Streamlit
    df_ready = []
    for row in data:
        df_ready.append({
            "ID": row.get("id"),
            "Business Segment": row.get("business_segment"),
            "Division": row.get("division"),
            "Kode Debtor": row.get("kode_debtor"),
            "Debtor Name": row.get("debtor_name"),
            "Sales Name": row.get("sales_name"),
            "ID POL": row.get("id_pol"),
            "ID POD": row.get("id_pod"),
            "Cabang Tagih": row.get("cabang_tagih"),
            "Alamat Kirim Invoice": row.get("alamat_kirim_invoice"),
            "Invoice Type": row.get("invoice_type"),
            "Dokumen Terkait": ", ".join(row.get("supporting_documents", []))  # list ke string
        })
    return df_ready

# ===== Tambah data =====
def insert_customer_data(values):
    (
        business_segment, division, kode_debtor, debtor_name, sales_name,
        id_pol, id_pod, cabang_tagih, alamat_kirim_invoice, invoice_type,
        dokumen_terkait
    ) = values

    dokumen_array = [d.strip() for d in dokumen_terkait.split(",") if d.strip()]  # convert jadi list

    data = {
        "business_segment": business_segment,
        "division": division,
        "kode_debtor": kode_debtor,
        "debtor_name": debtor_name,
        "sales_name": sales_name,
        "id_pol": id_pol,
        "id_pod": id_pod,
        "cabang_tagih": cabang_tagih,
        "alamat_kirim_invoice": alamat_kirim_invoice,
        "invoice_type": invoice_type,
        "supporting_documents": dokumen_array,
    }

    supabase.table("customer_guidance_invoice").insert(data).execute()

# ===== Hapus data berdasarkan ID =====
def delete_customer_data(id_list):
    for id in id_list:
        supabase.table("customer_guidance_invoice").delete().eq("id", id).execute()

# (Optional) Update data
def update_customer_data(id, data):
    (
        business_segment, division, kode_debtor, debtor_name, sales_name,
        id_pol, id_pod, cabang_tagih, alamat_kirim_invoice, invoice_type,
        dokumen_terkait
    ) = data

    dokumen_array = [d.strip() for d in dokumen_terkait.split(",") if d.strip()]

    update_data = {
        "business_segment": business_segment,
        "division": division,
        "kode_debtor": kode_debtor,
        "debtor_name": debtor_name,
        "sales_name": sales_name,
        "id_pol": id_pol,
        "id_pod": id_pod,
        "cabang_tagih": cabang_tagih,
        "alamat_kirim_invoice": alamat_kirim_invoice,
        "invoice_type": invoice_type,
        "supporting_documents": dokumen_array,
    }

    supabase.table("customer_guidance_invoice").update(update_data).eq("id", id).execute()

# === Cek jalan atau nggak ===
if __name__ == "__main__":
    print("INI DATA DARI SUPABASE:")
    data = fetch_customer_data()
    print(data)
