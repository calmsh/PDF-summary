import os  # OS 관련 기능을 사용하기 위한 표준 라이브러리
import openai  # OpenAI 공식 클라이언트 라이브러리 (버전 2.15.0 기준), API 키 검증에 활용
import streamlit as st  # 웹 앱을 손쉽게 만들 수 있는 프레임워크 (버전 1.29.0)
from PyPDF2 import PdfReader  # PDF 읽기 라이브러리 (버전 3.0.1)
# LangChain 관련 모듈: LLM 파이프라인 구성을 도와주는 프레임워크 (버전 0.3.27)
from langchain.text_splitter import CharacterTextSplitter  # 문서를 일정 단위로 자르는 유틸
from langchain_openai import OpenAIEmbeddings  # 텍스트 → 벡터 변환 (의미 기반 검색에 필요)
from langchain_openai import ChatOpenAI  # GPT 모델 호출 인터페이스
from langchain_community.vectorstores import FAISS  # 벡터를 저장하고 유사도 검색하는 DB
from langchain.chains.question_answering import load_qa_chain  # 문서 기반 QA 체인 로더
from langchain_community.callbacks import get_openai_callback  # 토큰 사용량 및 비용 트래킹


def validate_api_key(api_key: str) -> bool:
    """OpenAI API 키가 실제로 유효한지 확인하는 함수"""
    try:
        client = openai.OpenAI(api_key=api_key)
        client.models.list()  # 간단한 요청으로 키 활성화 여부 체크
        return True
    except Exception:
        return False


def build_vector_store(text: str, api_key: str):
    """추출된 텍스트를 청크로 분할하고 FAISS 벡터 DB를 구성하는 함수"""
    splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,    # 한 청크의 최대 글자 수
        chunk_overlap=200,  # 앞뒤 청크 간 겹치는 글자 수 (문맥 유지 목적)
        length_function=len,
    )
    chunks = splitter.split_text(text)
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", api_key=api_key)
    vector_db = FAISS.from_texts(chunks, embeddings)
    return vector_db


def main():
    # 페이지 기본 설정 (탭 제목 및 아이콘)
    st.set_page_config(page_title="전성현의 논문 초록 요약기", page_icon="�")
    st.title("� 전성현의 논문 초록 요약 서비스")
    st.caption("PDF를 업로드하면 AI가 핵심 내용을 자동으로 요약해드립니다.")
    st.divider()

    # ── 사이드바: API 키 설정 영역 ──────────────────────────────
    with st.sidebar:
        st.header("⚙️ 환경 설정")
        st.markdown("사용하려면 **OpenAI API 키**가 필요합니다.")
        api_key_input = st.text_input(
            label="API 키 입력",
            type="password",
            placeholder="sk-...",
            help="OpenAI 플랫폼에서 발급받은 Secret Key를 입력하세요.",
        )

        # API 키 상태 피드백
        if api_key_input:
            if validate_api_key(api_key_input):
                st.success("✅ API 키가 확인되었습니다!")
            else:
                st.error("❌ 유효하지 않은 키입니다. 다시 확인해 주세요.")
        else:
            st.info("🔑 위 입력란에 API 키를 넣어주세요.")

        st.markdown("---")
        st.markdown("🔗 [API 키 발급 바로가기](https://platform.openai.com/api-keys)")

    # ── 메인 영역: PDF 업로드 및 요약 처리 ──────────────────────
    uploaded_pdf = st.file_uploader(
        label="PDF 파일을 업로드하세요",
        type=["pdf"],
        help="텍스트가 포함된 PDF만 지원됩니다 (스캔 이미지 PDF 불가).",
    )

    if uploaded_pdf is not None:
        # API 키 검증 우선 확인
        if not api_key_input or not validate_api_key(api_key_input):
            st.warning("⚠️ 유효한 OpenAI API 키를 먼저 입력해 주세요.")
            st.stop()

        # PDF에서 전체 텍스트 추출
        reader = PdfReader(uploaded_pdf)
        raw_text = ""
        for page in reader.pages:
            raw_text += page.extract_text()

        # 벡터 DB 구성
        vector_db = build_vector_store(raw_text, api_key_input)

        # 요약 프롬프트
        summary_query = "업로드된 PDF 파일의 핵심 내용을 3~5문장으로 간결하게 요약해 주세요."

        # 유사 문서 검색 후 GPT 요약 실행
        relevant_docs = vector_db.similarity_search(summary_query)
        llm = ChatOpenAI(
            model="gpt-3.5-turbo-16k",
            api_key=api_key_input,
            temperature=0.1,  # 낮은 온도로 사실 기반 답변 유도
        )
        qa_chain = load_qa_chain(llm, chain_type="stuff")

        with st.spinner("🔍 PDF 내용을 분석하고 있습니다. 잠시만 기다려 주세요..."):
            with get_openai_callback() as cost_tracker:
                result = qa_chain.run(input_documents=relevant_docs, question=summary_query)

        # 결과 출력
        st.subheader("📋 요약 결과")
        st.write(result)
        st.markdown("---")
        st.caption(f"💰 이번 요약에 사용된 비용: **${cost_tracker.total_cost:.4f}**")


if __name__ == "__main__":
    main()  # 직접 실행 시에만 앱을 구동하도록 가드 처리