// inference_engine.js

// Data rules untuk diagnosa batuk
const rulesData = {
  "data_diagnosa_batuk": {
    "gejala": [
      {"kode": "G1", "nama": "Banyak lender ditenggorokan"},
      {"kode": "G2", "nama": "Tenggorokan gatal"},
      {"kode": "G3", "nama": "Tenggorokan sakit"},
      {"kode": "G4", "nama": "Bersin"},
      {"kode": "G5", "nama": "Sulit bernafas"},
      {"kode": "G6", "nama": "Hidung tersumbat"},
      {"kode": "G7", "nama": "Demam ringan"},
      {"kode": "G8", "nama": "Mata berair"},
      {"kode": "G9", "nama": "Batuk"},
      {"kode": "G10", "nama": "Sakit kepala"},
      {"kode": "G11", "nama": "Badan lemas"}
    ],
    "penyakit": [
      {"kode": "P1", "nama": "Batuk berdahak"},
      {"kode": "P2", "nama": "Batuk Kering"},
      {"kode": "P3", "nama": "Batuk Alergi"},
      {"kode": "GAGAL", "nama": "Tidak dapat didiagnosa"},
      {"kode": "UNKNOWN", "nama": "Tidak diketahui"}
    ],
    "aturan": [
      {"rule_id": "R1", "kode_penyakit": "P1", "cf_pakar": 0.8, "gejala": ["G1", "G4", "G6", "G8", "G9", "G10", "G11"]},
      {"rule_id": "R2", "kode_penyakit": "P2", "cf_pakar": 0.7, "gejala": ["G1", "G2", "G3", "G5", "G7", "G11"]},
      {"rule_id": "R3", "kode_penyakit": "P3", "cf_pakar": 0.6, "gejala": ["G1", "G2", "G5", "G8", "G9"]},
      {"rule_id": "R4", "kode_penyakit": "GAGAL", "cf_pakar": 0.9, "gejala": ["G4", "G2"]},
      {"rule_id": "R5", "kode_penyakit": "GAGAL", "cf_pakar": 0.9, "gejala": ["G3", "G1"]},
      {"rule_id": "R6", "kode_penyakit": "P3", "cf_pakar": 0.5, "gejala": ["G1", "G2", "G5", "G9"]},
      {"rule_id": "R7", "kode_penyakit": "P1", "cf_pakar": 0.6, "gejala": ["G1", "G4", "G6", "G9", "G11"]},
      {"rule_id": "R8", "kode_penyakit": "P2", "cf_pakar": 0.5, "gejala": ["G1", "G2", "G5", "G10", "G11"]},
      {"rule_id": "R9", "kode_penyakit": "KOMPLIKASI_P1", "cf_pakar": 0.6, "gejala": ["P1"]},
      {"rule_id": "R10", "kode_penyakit": "KOMPLIKASI_P2", "cf_pakar": 0.5, "gejala": ["P2"]},
      {"rule_id": "R11", "kode_penyakit": "KOMPLIKASI_P3", "cf_pakar": 0.4, "gejala": ["P3"]}
    ]
  }
};

// Inisialisasi ketika halaman dimuat
document.addEventListener('DOMContentLoaded', function() {
    tampilkanDaftarGejala();
    setupEventListeners();
});

// Menampilkan daftar gejala ke dalam form
function tampilkanDaftarGejala() {
    const daftarGejala = document.getElementById('daftar-gejala');
    const gejala = rulesData.data_diagnosa_batuk.gejala;
    
    let html = '';
    gejala.forEach(g => {
        html += `
            <div class="gejala-item">
                <label for="${g.kode}">${g.kode}: ${g.nama}</label>
                <select id="${g.kode}" class="cf-user-input" name="${g.kode}">
                    <option value="0">0 (Tidak yakin)</option>
                    <option value="0.2">0.2 (Sedikit yakin)</option>
                    <option value="0.4">0.4 (Cukup yakin)</option>
                    <option value="0.6">0.6 (Yakin)</option>
                    <option value="0.8">0.8 (Sangat yakin)</option>
                    <option value="1">1 (Pasti)</option>
                </select>
            </div>
        `;
    });
    
    daftarGejala.innerHTML = html;
}

// Setup event listeners
function setupEventListeners() {
    const form = document.getElementById('form-diagnosa');
    const modal = document.getElementById('myModal');
    const closeModal = document.getElementById('close-modal');
    
    // Event submit form
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        lakukanDiagnosa();
    });
    
    // Event close modal
    closeModal.addEventListener('click', function() {
        modal.style.display = 'none';
    });
    
    // Close modal ketika klik di luar modal
    window.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
}

// Fungsi untuk melakukan diagnosa menggunakan Certainty Factor
function lakukanDiagnosa() {
    const userCF = ambilInputUser();
    const hasilDiagnosa = hitungCertaintyFactor(userCF);
    
    tampilkanHasil(hasilDiagnosa);
}

// Mengambil input CF dari user
function ambilInputUser() {
    const userCF = {};
    const gejala = rulesData.data_diagnosa_batuk.gejala;
    
    gejala.forEach(g => {
        const selectElement = document.getElementById(g.kode);
        userCF[g.kode] = parseFloat(selectElement.value);
    });
    
    return userCF;
}

// Menghitung Certainty Factor
function hitungCertaintyFactor(userCF) {
    const aturan = rulesData.data_diagnosa_batuk.aturan;
    const penyakit = rulesData.data_diagnosa_batuk.penyakit;
    
    let hasilPenyakit = {};
    
    // Inisialisasi hasil untuk setiap penyakit
    penyakit.forEach(p => {
        if (p.kode !== "UNKNOWN") {
            hasilPenyakit[p.kode] = {
                kode: p.kode,
                nama: p.nama,
                cf_akhir: 0,
                rules_terpenuhi: []
            };
        }
    });
    
    // Proses setiap rule
    aturan.forEach(rule => {
        if (rule.kode_penyakit.startsWith("KOMPLIKASI")) {
            // Handle rules komplikasi (jika diperlukan)
            return;
        }
        
        const gejalaRule = rule.gejala;
        let cf_rule = rule.cf_pakar;
        let cf_user_combined = 1;
        let semuaGejalaAda = true;
        
        // Hitung CF user untuk gejala dalam rule ini
        gejalaRule.forEach(kodeGejala => {
            if (kodeGejala.startsWith("G")) {
                if (userCF[kodeGejala] !== undefined) {
                    cf_user_combined *= (1 - userCF[kodeGejala]);
                } else {
                    semuaGejalaAda = false;
                }
            }
        });
        
        if (semuaGejalaAda) {
            cf_user_combined = 1 - cf_user_combined;
            const cf_akhir = cf_rule * cf_user_combined;
            
            if (cf_akhir > hasilPenyakit[rule.kode_penyakit].cf_akhir) {
                hasilPenyakit[rule.kode_penyakit].cf_akhir = cf_akhir;
                hasilPenyakit[rule.kode_penyakit].rules_terpenuhi.push(rule.rule_id);
            }
        }
    });
    
    // Cari penyakit dengan CF tertinggi
    let penyakitTerbaik = null;
    let cfTertinggi = -1;
    
    Object.values(hasilPenyakit).forEach(p => {
        if (p.cf_akhir > cfTertinggi) {
            cfTertinggi = p.cf_akhir;
            penyakitTerbaik = p;
        }
    });
    
    // Jika tidak ada penyakit yang memenuhi, kembalikan UNKNOWN
    if (!penyakitTerbaik || cfTertinggi <= 0) {
        return {
            kode: "UNKNOWN",
            nama: "Tidak diketahui",
            cf_akhir: 0,
            confidence: "Rendah",
            rekomendasi: "Gejala yang dimasukkan tidak cukup untuk diagnosa. Silakan konsultasi dengan dokter."
        };
    }
    
    // Tentukan tingkat confidence
    let confidence = "Rendah";
    if (cfTertinggi >= 0.7) confidence = "Tinggi";
    else if (cfTertinggi >= 0.4) confidence = "Sedang";
    
    return {
        kode: penyakitTerbaik.kode,
        nama: penyakitTerbaik.nama,
        cf_akhir: cfTertinggi,
        confidence: confidence,
        rekomendasi: generateRekomendasi(penyakitTerbaik.kode)
    };
}

// Generate rekomendasi berdasarkan jenis penyakit
function generateRekomendasi(kodePenyakit) {
    const rekomendasi = {
        "P1": 'Berdasarkan hasil diagnosa, Anda kemungkinan mengalami Batuk berdahak.',

        "P2": `Berdasarkan hasil diagnosa, Anda kemungkinan mengalami Batuk kering.`,

        "P3": `Berdasarkan hasil diagnosa, Anda kemungkinan mengalami Batuk alergi.`,

        "GAGAL": `Tidak dapat didiagnosa dengan pasti:
                • Gejala yang dimasukkan bertentangan
                • Silakan konsultasi langsung dengan dokter
                • Periksa gejala yang dialami lebih detail`,


       "UNKNOWN": `Tidak dapat menentukan diagnosa:
                • Gejala tidak spesifik
                • Disarankan konsultasi dengan dokter
                • Perhatikan perkembangan gejala`
    };
    
    return rekomendasi[kodePenyakit] || rekomendasi["UNKNOWN"];
}

// Menampilkan hasil diagnosa dalam modal
function tampilkanHasil(hasil) {
    const modal = document.getElementById('myModal');
    const resultText = document.getElementById('diagnosis-result-text');
    
    let hasilText = `
Jenis Batuk: ${hasil.nama}
Tingkat Keyakinan: ${(hasil.cf_akhir * 100).toFixed(2)}%
Confidence: ${hasil.confidence}

${hasil.rekomendasi}

Catatan: Hasil diagnosa ini bersifat perkiraan berdasarkan gejala yang dimasukkan. 
Disarankan untuk konsultasi dengan dokter untuk diagnosa yang lebih akurat.
    `;
    
    resultText.textContent = hasilText;
    modal.style.display = 'block';
}