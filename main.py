import os
import streamlit as st
from mistralai import Mistral
import json

# マトリックス風のカスタムCSS（背景、文字色、カード風のスタイル）
st.markdown(
    """
    <style>
    .stApp {
        background-color: black;
        color: #00FF00;
    }
    .stButton>button {
        background-color: #000000;
        color: #00FF00;
        border: 1px solid #00FF00;
    }
    .stTextArea textarea {
        background-color: #000000;
        color: #00FF00;
    }
    .card {
        background-color: #000000;
        color: #00FF00;
        border: 2px solid #00FF00;
        padding: 10px;
        border-radius: 8px;
        margin: 10px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def generate_with_reflection(input_text, client, model):
    prompt = f"""
あなたは未来を予見する占い師であり、因果関係の分析のエキスパートです。これから以下の手順に従って、ユーザーの入力された出来事・状況に基づく、従来の
常識を覆すような、非常に意外で驚愕すべき未来のシナリオを生成してください.

【手順】
1. 【初期生成】:
   - 入力された出来事・状況に基づき、通常では想像もできないが、全くありえないわけではない、極めて意外な未来の帰結を1個生成してください.
   - その帰結に至るまでの、論理的でありながらも従来の常識を覆す因果関係の各ステップを、配列として詳細に説明してください.
   - この情報は "initial_generation" オブジェクトの "outcome" フィールドに帰結を、"causal_steps" フィールドに各ステップを配列として示してください.
2. 【Reflection】:
   - 【初期生成】で得られた帰結と因果関係の各ステップについて、あなた自身が熟考し、帰結が入力された出来事・状況に比べてどれほど意外か、また各因果ステップが十分に合理的かつ驚きの要素を持っているかを評価してください.
   - 評価結果は "reflection" オブジェクトの "evaluation" フィールドに、さらに改善の余地がある場合の改善提案は "improvements" フィールドに示してください.
3. 【最終結果】:
   - 【初期生成】と【Reflection】の内容を踏まえて、最終的な帰結と因果関係の各ステップを、意外性と合理性の両面で最も優れた最終案として提示してください.
   - "final_result" オブジェクトの "outcome" フィールドに帰結を、"causal_steps" フィールドに各ステップを配列として示してください.

【入力された出来事・状況】
"{input_text}"

以下のJSON形式に従って、結果を出力してください:
{{
  "initial_generation": {{
      "outcome": "<初期生成された帰結>",
      "causal_steps": ["<因果ステップ1>", "<因果ステップ2>", "..."]
  }},
  "reflection": {{
      "evaluation": "<Reflectionの評価>",
      "improvements": "<Reflectionの改善提案>"
  }},
  "final_result": {{
      "outcome": "<最終的な帰結>",
      "causal_steps": ["<因果ステップ1>", "<因果ステップ2>", "..."]
  }}
}}

【重要】
- 出力されるJSONは1行のコンパクトな形式でなければなりません.
- すべての制御文字（改行、タブなど）は必ず「\\n」のようにエスケープされ、余計なスペースや改行を含めないでください.
- 出力は上記のJSONオブジェクトのみを返してください.
"""
    response = client.chat.complete(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=1.0,
        top_p=0.9
    )
    return response.choices[0].message.content

# テキストエリアの初期値（例となる出来事・状況）
default_example = "例: 高校時代のある日、突然校庭に奇妙な光が現れ、友人とその現象を追跡した結果、予想もしなかった大きな秘密に辿り着いた。"

# Streamlit UI：タイトルなどの不要な固定テキストは表示せず、テキストエリアのみに例を設定
input_text = st.text_area("", value=default_example, height=150)

if st.button("シナリオ生成"):
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        st.error("MISTRAL_API_KEYが設定されていません。環境変数を確認してください。")
    else:
        model = "open-mistral-nemo"
        client = Mistral(api_key=api_key)
        with st.spinner("シナリオを生成中..."):
            final_result = generate_with_reflection(input_text, client, model)
            final_result = final_result.replace("```json", "").replace("```", "")
            try:
                result_json = json.loads(final_result.strip())
                #st.json(result_json)  # JSON全体の結果（任意）
                final_outcome = result_json.get("final_result", {}).get("outcome", "")
                causal_steps = result_json.get("final_result", {}).get("causal_steps", [])
                
                if causal_steps or final_outcome:
                    # 各因果ステップをカード形式のエクスパンダーで表示（タイトルなし）
                    for step in causal_steps:
                        with st.expander(""):
                            card_html = f"""
                            <div class="card">
                                <p>{step}</p>
                            </div>
                            """
                            st.markdown(card_html, unsafe_allow_html=True)
                    # 最後の因果ステップのあとに Final Outcome をカード形式で表示（タイトルなし）
                    with st.expander(""):
                        card_html = f"""
                        <div class="card">
                            <p>{final_outcome}</p>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
                else:
                    st.write("因果関係のステップまたは最終帰結が見つかりませんでした。")
            except json.JSONDecodeError as e:
                st.error("JSONのパースエラーが発生しました:")
                st.write("Raw output:", final_result)

