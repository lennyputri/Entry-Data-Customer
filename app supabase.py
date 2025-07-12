import streamlit as st
from dbsupabase import fetch_customer_data, insert_customer_data, delete_customer_data
import pandas as pd

# ==== Harus di paling atas ====
st.set_page_config(page_title="Customer Guidance Invoicing", layout="wide")

# ==== Inisialisasi state untuk fitur edit ==== 
#if "edit_mode" not in st.session_state:
#    st.session_state.edit_mode = False
#if "edit_data" not in st.session_state:
#    st.session_state.edit_data = None
if "menu" not in st.session_state:
    st.session_state.menu = "📄 Lihat Data"

# ==== CSS Styling ====
def show_centered_alert(message, color="green"):
    bg_color = "#d4edda" if color == "green" else "#f8d7da"
    border_color = "#2e7d32" if color == "green" else "#b71c1c"
    text_color = "#155724" if color == "green" else "#721c24"

st.markdown("""
    <style>
        /* Tambahan untuk border merah password */
        input:invalid {
            box-shadow: none !important;
            outline: none !important;
        }

        div[data-baseweb="input"] input {
            border: none !important;
            outline : none !important;
            padding: 8px;
            background-color: transparent;
            color : black:
        }

        div[data-baseweb="input"] {
            border: 2px solid #d90429;
            border-radius: 8px;
            background-color: white;
            padding: 4px;
        }
        
        /* Input dan Textarea */
        div[data-baseweb="input"] input,
        div[data-baseweb="textarea"] textarea,
        div[data-baseweb="select"] {
            background-color: #ffffff;
            color: black;
            border: 2px solid #d90429;
            border-radius: 8px;
            padding: 8px;
        }

        /* Label */
        label {
            font-weight: bold;
            color: white !important;
        }

        /* Background form box */
        div[data-testid="stForm"] {
            background-color: #0A2647;
            padding: 30px;
            border-radius: 15px;
        }

        /* Tombol Submit */
        button[kind="primary"] {
            background-color: #d90429;
            color: white;
            font-weight: bold;
            border-radius: 8px;
        }

        button[kind="primary"]:hover {
            background-color: #a4001d;
            color: white;
        }

        /* Sidebar background */
        section[data-testid="stSidebar"] {
            background-color: #0A2647;
            color: white;
        }

        /* Sidebar radio button label */
        section[data-testid="stSidebar"] label {
            color: white !important;
            font-weight: bold;
        }

        /* Warna teks radio button */
        section[data-testid="stSidebar"] .stRadio div {
            color: white !important;
        }

        /* Warna ikon dan teks radio */
        section[data-testid="stSidebar"] svg, 
        section[data-testid="stSidebar"] span {
            color: white !important;
            fill: white !important;
        }

        /* Jika radio terlihat seperti 'mati' */
        section[data-testid="stSidebar"] .css-1n76uvr {
            opacity: 1 !important;
        }

        /* Judul utama */
        h1 {
            color: #0A2647;
        }

    </style>
""", unsafe_allow_html=True)

# ==== Header & Sidebar ====
st.markdown(
    '<img src="https://www.freight-hub.co/wp-content/uploads/2023/11/Logo-MGLog.png.webp" width="240"/>',
    unsafe_allow_html=True
)
st.title("Form Kebutuhan Dokumen Invoice Customer")

menu = st.sidebar.radio("Menu", ["📂 Lihat Data", "🖥️ Entri Data Baru"], 
                        index=0 if st.session_state.menu == "📂 Lihat Data" else 1)

# ==== Proteksi Admin untuk Fitur Hapus ====
is_admin = False
with st.sidebar.expander("🔐 Login Admin untuk Hapus Data"):
    password = st.text_input("Masukkan Password Admin:", type="password")
    if password == st.secrets["ADMIN_PASSWORD"]:
        is_admin = True
        st.markdown("""
            <div style='background-color: #d4edda; border: 2px solid #2e7d32;
                        padding: 12px; border-radius: 8px; color: #2e7d32;
                        font-weight: bold;'>
                ✅ Login Admin berhasil!
                </div>
        """, unsafe_allow_html=True)
    elif password != "":
        st.markdown("""
            <div style='background-color: #f8d7da; border: 2px solid #b71c1c;
                        padding: 12px; border-radius: 8px; color: #b71c1c;
                        font-weight: bold;'>
                ❌ Password Admin salah !
            </div>
        """, unsafe_allow_html=True)

# ==== Lihat Data ====
if menu == "📂 Lihat Data":
    st.subheader("📋 Data Kebutuhan Dokumen Invoice Customer")
    data = fetch_customer_data()
    if data:
        df = pd.DataFrame(data, columns=[
            "ID", "Business Segment", "Division", "Kode Debtor", "Debtor Name",
            "Sales Name", "ID POL", "ID POD", "Cabang Tagih", "Alamat Kirim Invoice",
            "Invoice Type", "Dokumen Terkait"
        ])

        # State untuk data yang sedang ditampilkan
        if 'df_display' not in st.session_state:
            st.session_state.df_display = df.copy()

        # SEARCH BOX UNTUK DEBTOR NAME
        # Ambil list debtor unik dari dataframe
        debtor_names = sorted(st.session_state.df_display['Debtor Name'].dropna().unique())

        selected_debtor = st.selectbox(
            "Pilih atau cari Debtor Name:",
            options=["Semua"] + sorted(debtor_names),
            index=0,
        )

        # Filter dataframe berdasarkan pilihan
        if selected_debtor != "Semua":
            filtered_df = st.session_state.df_display[
                st.session_state.df_display['Debtor Name'] == selected_debtor
            ]
        else:
            filtered_df = st.session_state.df_display
        
        st.dataframe(filtered_df, use_container_width=True)

        #Garis Pemisah Visual
        st.markdown("---")

        # Proteksi admin: hanya tampil jika login berhasil
        # ===== Pilih baris + klik tombol pertama ======
        if is_admin:
            st.markdown("### Hapus Baris")
        
            ids_to_delete = st.multiselect(
                "Pilih baris yang ingin dihapus (berdasarkan ID):",
                options=filtered_df['ID'].tolist()
            )
            
            if st.button("Hapus Data Terpilih", disabled=len(ids_to_delete) == 0):
                # simpan pilihan & munculkan dialog konfirmasi
                st.session_state.ids_to_delete = ids_to_delete
                st.session_state.show_confirm = True
                
        # ===== Dialog Konfirmasi =======        
        if st.session_state.get("show_confirm", False):          
            with st.expander("", expanded=True):
                # Judul custom
                st.markdown(
                    "<div style='font-size:22px; font-weight:bold; color:#0a0101; margin-bottom:10px;'>⚠️ Konfirmasi Hapus</div>",
                    unsafe_allow_html=True
                )

                # Box pesan konfirmasi
                st.markdown(
                    f"""
                    <div style="background-color:#fedddb; padding:10px; border:2px solid #bd0606; border-radius:12px; margin-bottom:20px;">
                        <strong style="color:#d90429; font-size:16px;">
                            Apakah Anda yakin ingin menghapus data dengan ID:
                            <span style="color:#d90429;">{st.session_state.get("ids_to_delete", [])}</span>
                        </strong>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                col1, col2 = st.columns(2)

                # Tombol konfirmasi & batal
                if col1.button("✅ Ya, Hapus Sekarang", key="confirm_delete"):
                    st.session_state.confirm_click = True
                if col2.button("❌ Batal", key="cancel_delete"):
                    st.session_state.confirm_click = False
                    st.session_state.show_confirm = False
                    st.info("Penghapusan dibatalkan.")
                    st.rerun()
                
                # ---- Eksekusi hapus setelah tombol ditekan ----
                if st.session_state.get("confirm_click", None):
                    delete_customer_data(st.session_state.ids_to_delete)

                    # refresh data dari Supabase
                    data = fetch_customer_data()
                    st.session_state.df_display = pd.DataFrame(
                        data,
                        columns=[
                            "ID", "Business Segment", "Division", "Kode Debtor",
                            "Debtor Name", "Sales Name", "ID POL", "ID POD",
                            "Cabang Tagih", "Alamat Kirim Invoice",
                            "Invoice Type", "Dokumen Terkait"
                        ]
                    )
                                 
                    st.success(
                        f"Berhasil menghapus baris dengan ID: {st.session_state.ids_to_delete}"
                    )
                    # bersihkan state dan reload tampilan
                    st.session_state.show_confirm = False
                    st.session_state.confirm_click = None
                    st.session_state.ids_to_delete = []
                    st.rerun()
        else:
            st.markdown("🔒 Fitur hapus data hanya untuk admin. Login di sidebar untuk akses.")

# ==== Entri Baru ====
elif menu == "🖥️ Entri Data Baru":
   
    #Ambil state untuk edit mode
    edit_mode = False
    edit_data = {}

    # === Mapping 4 perusahaan untuk isi otomatis ===
    data_customer_mapping = {
        "MATAHARI PUTRA PRIMA TBK, PT": {
            "Kode Debtor": "CST-0003041",
            "Sales Name": "Hanna Manalu",
            "Alamat Kirim Invoice": '''JL. RAYA SERANG KM 26.5 TOBAT, BALARAJA TANGERANG, BANTEN, 15610, TUKAR FAKTUR SETIAP SENIN RECC : CIBITUNG BPK OKTAF (MPP CHILLER) KAWASAN INDUSTRI MM2100, JL. SELAYAR II NO.3 TELAJUNG, CIKARANG BARAT, BEKASI, JAWA BARAT 17530 TELP : +62 813-1123-5087'''
        },
        "INDOFOOD FORTUNA MAKMUR, PT": {
            "Kode Debtor": "CST-0013198",
            "Sales Name": "Reyda Ferdila",
            "Alamat Kirim Invoice": "DIKIRIM SAMA CABANG SEMARANG"
        },
        "TIRTAKENCANA TATAWARNA, PT": {
            "Kode Debtor": "CST-0023282",
            "Sales Name": "Kevin Tanoyo",
            "Alamat Kirim Invoice": "Jl. Raya Ahmad Yani No. 317 Dukuh Menanggal – Surabaya ATTN : IBU ANISSA / IBU RIA"
        },
        "INDOMARCO ADI PRIMA, PT": {
            "Kode Debtor": "CST-0010342",
            "Sales Name": "Hanna Manalu",
            "Alamat Kirim Invoice": '''Jl. Jababeka Raya Blok A No. 6-15 Cikarang Utara – Bekasi - Up : Bp. Agusnadi / Bp. Sujartomo  
            EMAIL : "agusnadi@indomarco.co.id"'''
        }
    }

    # ========= HANDLE PEMILIHAN DEBTOR =========
    debtor_names_list = ["Pilih Debtor"] + list(data_customer_mapping.keys())

    if "selected_debtor" not in st.session_state:
        st.session_state.selected_debtor = "Pilih Debtor"

    # Kosongkan label selectbox biar gak dobel
    selected_debtor = st.selectbox("Debtor Name".upper(),
        options=debtor_names_list,
        index=debtor_names_list.index(st.session_state.selected_debtor),
    )

    if selected_debtor != st.session_state.selected_debtor:
        st.session_state.selected_debtor = selected_debtor
        st.rerun()

    # Ambil data sesuai debtor
    debtor_data = data_customer_mapping.get(st.session_state.selected_debtor, {})
    kode_debtor = debtor_data.get("Kode Debtor", "")
    sales_name = debtor_data.get("Sales Name", "")
    alamat_kirim_invoice = debtor_data.get("Alamat Kirim Invoice", "")

    # ========= FORM =========
    with st.form("form_customer_invoice"):
        col1, col2 = st.columns(2)
        with col1:
            business_segment = st.selectbox("Business Segment*".upper(), ["Domestic", "International"])
            division = st.selectbox("Division*".upper(),["Sea Freight", "Air Freight", "Custom", "Industrial Project", "Wh and Transport"])                    
            id_pol_pod_cabangtagih_options = ["IDAMP", "IDAMQ", "IDBDJ", "IDBIT", "IDBLW", "IDBPN", "IDENE", "IDGTO", "IDJKT", "IDKDI", "IDKID", "IDKOE",
                                              "IDKTG", "IDLBO", "IDMKS", "IDMOF", "IDOTH", "IDPAP", "IDPDG", "IDPKX", "IDPNK", "IDPTL", "IDPWG", "IDSMG", "IDSMQ",
                                              "IDSRI", "IDSUB", "IDTKG", "IDTLI", "IDTRK", "IDTTE", "IDWIN"]
            id_pol = st.selectbox("ID POL*".upper(), ["Select"] + id_pol_pod_cabangtagih_options)
            id_pod = st.selectbox("ID POD*".upper(), ["Select"] + id_pol_pod_cabangtagih_options)
            cabang_tagih = st.selectbox("Cabang Tagih*".upper(),["Select"] +  id_pol_pod_cabangtagih_options)
        with col2:
            st.text_input("Kode Debtor*".upper(), value=kode_debtor, disabled=True)
            st.text_input("Sales Name*".upper(), value=sales_name, disabled=True)
            st.text_area("Alamat Kirim Invoice*".upper(), value=alamat_kirim_invoice, height=110, disabled=True)
            invoice_type = st.selectbox("Invoice Type*".upper(), ["Select"] + ["Hardcopy", "Softcopy"])
            dokumen_dipilih = st.multiselect("Supporting Documents*".upper(), ["KWITANSI", "REKAPAN", "INV", "FP", "RESI", "BATSB", "SI", "BL", "SURAT JALAN", "SJ PABRIK"])
            dokumen_tambahan = st.text_input("Tambah Dokumen Lain (pisahkan dengan koma)".upper())
            st.caption("Kosongkan jika tidak ada dokumen tambahan.")

            # Gabung semua dokumen jadi satu list
            if dokumen_tambahan:
                dokumen_tambahan_list = [d.strip().upper() for d in dokumen_tambahan.split(",") if d.strip()]
            else:
                dokumen_tambahan_list = []

            dokumen_terkait = dokumen_dipilih + dokumen_tambahan_list


        submitted = st.form_submit_button("SIMPAN DATA")
        if submitted:
            # Validasi kolom wajib
            if (
                not business_segment or
                not division or
                not kode_debtor.strip() or
                not st.session_state.selected_debtor.strip() or
                not sales_name.strip() or
                id_pol == "Select" or
                id_pod == "Select" or
                cabang_tagih == "Select" or
                not alamat_kirim_invoice.strip() or
                invoice_type == "Select" or
                not dokumen_terkait
            ):
                st.markdown("""
                    <div style='background-color: white; padding: 15px; border-radius: 10px;'>
                        <span style='color: red; font-weight: bold;'>❌ Terdapat data yang belum diisi. Harap lengkapi semua kolom wajib.</span>
                    </div>
                """, unsafe_allow_html=True)
            else:
                insert_customer_data((
                        business_segment, division, kode_debtor.strip(), st.session_state.selected_debtor.strip(), sales_name.strip(),
                        id_pol, id_pod, cabang_tagih.strip(), alamat_kirim_invoice.strip(), invoice_type, dokumen_terkait
                ))
                st.markdown("<div style='background-color:white; color:green; padding:10px;'>✅ Data Customer Guidance Invoicing berhasil disimpan.</div>", unsafe_allow_html=True)
