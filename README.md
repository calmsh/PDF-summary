# 📑 전성현의 논문 요약 서비스


## 1. 프로젝트 소개

**만든 이유:**  
논문이나 보고서 PDF를 처음부터 끝까지 읽는 건 시간이 많이 걸립니다. 이 프로젝트는 LangChain 기반 RAG(Retrieval-Augmented Generation) 파이프라인을 활용해 PDF에서 핵심 내용을 자동으로 추출·요약해주는 웹 서비스입니다. 긴 문서도 3~5문장으로 빠르게 파악할 수 있게 도와줍니다.

**주요 기능:**
- OpenAI API 키 입력 및 실시간 유효성 검증
- PDF 업로드 후 페이지 전체 텍스트 자동 추출 (`PyPDF2` 사용)
- 텍스트 청킹 → 임베딩 → `FAISS` 벡터 DB 구성
- GPT 기반 맞춤형 요약 생성 (3~5문장 분량)
- 요약 완료 후 API 호출 비용 표시

---

## 2. 로컬 실행 방법

아래 순서대로 진행하면 로컬 환경에서도 앱을 실행할 수 있습니다.

```bash
# 1. 저장소 클론
git clone https://github.com/calmsh/PDF-summary

# 2. 가상환경 생성 및 활성화 (권장)
python -m venv venv

# Windows (cmd):
venv\Scripts\activate
# Windows (PowerShell):
venv\Scripts\Activate.ps1
# Mac / Linux:
source venv/bin/activate

# 3. 의존 패키지 일괄 설치
pip install -r requirements.txt

# 4. 앱 실행
streamlit run make_pdf_summary_site.py
```

---

## 3. 자주 발생하는 문제와 해결법

앱 사용 중 오류가 생기면 아래 항목을 먼저 확인해 보세요.

- **"유효하지 않은 키입니다." 메시지가 뜰 때:**  
  [OpenAI API 키 페이지](https://platform.openai.com/api-keys)에서 발급한 Secret Key인지 확인하고, 앞뒤 공백이나 오타가 없는지 점검하세요.

- **결제 관련 오류 (크레딧 부족 등):**  
  무료 크레딧이 소진되거나 결제 수단이 미등록 상태일 수 있습니다. OpenAI 사용량 대시보드에서 잔액과 한도를 확인하세요.



