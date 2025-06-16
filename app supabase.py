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
    st.subheader("📋 Data Customer Guidance Invoicing")
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
            with st.expander("⚠️ Konfirmasi Hapus", expanded=True):
                st.markdown(
                    f"""
                    <div style="background-color:#dbeafe; padding:15px; border:2px solid #2563eb; border-radius:12px;">
                        <strong style="color:#1e3a8a; font-size:16px;">
                            Apakah Anda yakin ingin menghapus data dengan ID:
                            <span style="color:#1d4ed8;">{st.session_state.get("ids_to_delete", [])}</span>
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
    st.subheader("📝 Tambah Data Customer Guidance Invoicing")
    
    #Ambil state untuk edit mode
    edit_mode = False
    edit_data = {}

    with st.form("form_customer_invoice"):
        col1, col2 = st.columns(2)
        with col1:
            business_segment = st.selectbox(
                "Business Segment".upper(), 
                ["Domestic", "International"],
                index=["Domestic", "International"].index(edit_data["Business Segment"]) if edit_mode else 0
            )
            division = st.selectbox(
                "Division".upper(),
                ["Sea Freight", "Air Freight", "Custom", "Industrial Project", "Wh and Transport"],
                index=["Sea Freight", "Air Freight", "Custom", "Industrial Project", "Wh and Transport"].index(
                edit_data.get("Division", "Sea Freight"))
            )
            kode_debtor = st.text_input(
                "Kode Debtor".upper(),
                value=edit_data.get("Kode Debtor", "")
            )
            debtor_name = st.text_input(
                "Debtor Name".upper(),
                value=edit_data.get("Debtor Name", "")
            )
            sales_name = st.text_input(
                "Sales Name".upper(),
                value=edit_data.get("Debtor Name", "")
            )
            id_pol_pod_cabangtagih_options = ["IDAMP", "IDAMQ", "IDBDJ", "IDBIT", "IDBLW", "IDBPN", "IDENE", "IDGTO", "IDJKT", "IDKDI", "IDKID", "IDKOE",
                                              "IDKTG", "IDLBO", "IDMKS", "IDMOF", "IDOTH", "IDPAP", "IDPDG", "IDPKX", "IDPNK", "IDPTL", "IDPWG", "IDSMG", "IDSMQ",
                                              "IDSRI", "IDSUB", "IDTKG", "IDTLI", "IDTRK", "IDTTE", "IDWIN"]
            id_pol = st.selectbox(
                "ID POL".upper(), ["Select"] + id_pol_pod_cabangtagih_options,
                index=(["Select"] + id_pol_pod_cabangtagih_options).index(edit_data.get("ID POL", "Select"))
            )
            id_pod = st.selectbox(
                "ID POD".upper(), ["Select"] + id_pol_pod_cabangtagih_options,
                index=(["Select"] + id_pol_pod_cabangtagih_options).index(edit_data.get("ID POD", "Select"))
            )

        with col2:
            cabang_tagih = st.selectbox(
                "Cabang Tagih".upper(), ["Select"] + id_pol_pod_cabangtagih_options,
                index=(["Select"] + id_pol_pod_cabangtagih_options).index(
                    edit_data.get("Cabang Tagih", "Select"))
            )
            alamat_kirim_invoice = st.text_area(
                "Alamat Kirim Invoice".upper(),
                value=edit_data.get("Alamat Kirim Invoice", ""), height=150
            )
            invoice_type = st.selectbox(
                "Invoice Type".upper(), ["Select"] + ["Hardcopy", "Softcopy"],
                index=["Select", "Hardcopy", "Softcopy"].index(edit_data.get("Invoice Type", "Select"))
            )
            document_options = ["KWITANSI", "REKAPAN", "INV FP", "RESI", "BATSB", "SI", "BL"]
            dokumen_dipilih = st.multiselect(
                "Supporting Documents".upper(), document_options,
                default=[d.strip() for d in edit_data.get("Dokumen Terkait", "").split(",") if d.strip()
                         if d.strip() in document_options]
            )
            
            dokumen_tambahan = st.text_input("Tambah Dokumen Lain (pisahkan dengan koma jika lebih dari satu)".upper())
            st.caption("Kosongkan jika tidak ada dokumen tambahan.")

            # Gabung semua dokumen jadi satu list
            if dokumen_tambahan:
                dokumen_tambahan_list = [d.strip() for d in dokumen_tambahan.split(",") if d.strip()]
            else:
                dokumen_tambahan_list = []

            dokumen_terkait = dokumen_dipilih + dokumen_tambahan_list


        submitted = st.form_submit_button("SIMPAN DATA")
        if submitted:
            # Validasi kolom wajib
            if not all([
                business_segment, division, kode_debtor.strip(), debtor_name.strip(), sales_name.strip(),
                id_pol, id_pod, cabang_tagih.strip(), alamat_kirim_invoice.strip(), invoice_type, dokumen_terkait
            ]):
                st.markdown("""
                    <div style='background-color: white; padding: 15px; border-radius: 10px;'>
                        <span style='color: red; font-weight: bold;'>❌ Terdapat data yang belum diisi. Harap lengkapi semua kolom wajib.</span>
                    </div>
                """, unsafe_allow_html=True)
            else:
                insert_customer_data((
                        business_segment, division, kode_debtor.strip(), debtor_name.strip(), sales_name.strip(),
                        id_pol, id_pod, cabang_tagih.strip(), alamat_kirim_invoice.strip(), invoice_type, ", ".join(dokumen_terkait)
                ))
                st.markdown("<div style='background-color:white; color:green; padding:10px;'>✅ Data Customer Guidance Invoicing berhasil disimpan.</div>", unsafe_allow_html=True)
