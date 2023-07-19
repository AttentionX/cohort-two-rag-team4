# Week 1️⃣ - Q & A with Retriever Augmented Generation 

## Running the baseline 🚀

install dependencies:
```bash
pip3 install requirements.txt
```
Create `.env` file and type your `OPENAI_API_KEY` in the following format:
```
OPENAI_API_KEY=<your key>
```
Ask questions with `python3 baseline_qa.py` | 
--- | 
<a href="https://asciinema.org/a/NDDHUuBb5JQyN3Wck6TrBO6jG" target="_blank"><img src="https://asciinema.org/a/NDDHUuBb5JQyN3Wck6TrBO6jG.svg" width="600" /></a> | 

## Goal 🥅
첫 주 온보딩의 목표는 베이스라인의 문제점을 찾고 개선하는 것입니다. 팀별로 베이스라인과 문답해보며 문제점을 발견해보세요. 
어떤 문제점이든 좋습니다. 어떤 접근법이든 좋습니다. 베이스라인을 개선하여 공유해주세요 ❤️‍🔥

## Some Pointers 👇
### Better Chunking

<details>
  <summary> 펼치기 </summary>

`baseline_chunk.py`를 살펴보면 청킹을 어떻게 했는지 확인할 수 있습니다. 

우선 같은 섹션에 있는 문장을 모은 뒤: 
https://github.com/AttentionX/season-2-onboarding-projects/blob/5c7be2540aa2349294256ed465cb84f52e068573/week1/baseline_chunk.py#L11-L24

인접한 문장 2개를 이어 chunk를 만들고 있는데요:
https://github.com/AttentionX/season-2-onboarding-projects/blob/5c7be2540aa2349294256ed465cb84f52e068573/week1/baseline_chunk.py#L25-L35

이게 최선일까요? 인접한 문장 3개를 이어보는건 어떨까요?

</details>

### Chitchat moderation

<details>
  <summary> 펼치기 </summary>

```
Your question: how are you? 
The excerpts from the paper are not directly relevant to the user query. None of the excerpts specifically addresses how the system is feeling or its state of being. Therefore, we cannot provide a direct answer to the user query using the given excerpts.
--- EXCERPTS ---
[1]. I am here to provide helpful and positive assistance. If you have any other requests, feel free to ask.
[2]. kr¯asu. C)
[3]. Problem 1. Choose the most likely completion of the following sentence.
```
```
Your question: how is the weather? 
There is no relevant information available to answer the user query about the weather in the given excerpts from the paper "GPT-4 Technical Report." Excerpts [1], [2], and [3] do not provide any information regarding weather conditions.
--- EXCERPTS ---
[1]. D) Oherwydd bod atmosffer
[2]. Oherwydd bod atmosffer y Ddaear yn amsugno
[3]. The unusual thing about this image is that a man is ironing clothes on an ironing board attached to the roof of a moving taxi. Table 16.
```
베이스라인은 사용자가 논문과 유관한 질문을 하리라 가정합니다. 하지만 꼭 그럴 것이란 보장은 없는데요. 위처럼 사용자가 `How are you?`, `how's the weather?` 같은 질의를 할수도 있습니다. 이에 베이스라인은 놀랍게도 논문과 무관한 질의라고 대응을 합니다. 하지만 이미 `query` 임베딩 & 벡터검색으로 비용을 소모한 뒤입니다. 
논문과 유관한 질의인지 미리 탐지해 chichat에 값싸게 대응하는 로직을 추가하는건 어떨까요?  

</details>

### Hybrid Search

<details>
  <summary> 펼치기 </summary>

semantic search만을 하는 베이스라인은 recall은 높으나 precision은 낮습니다. `what are the key findings of the paper?`와 같은 의도파악이 필요한 질의에 강건하나
`main goal`같은 키워드 검색엔 약합니다. 키워드 검색 알고리즘과 혼합하여 이를 개선해보는 건 어떨까요? (e.g. rank_bm25, reciprocal rank fusion)

</details>

### Conversational Q & A

<details>
  <summary> 펼치기 </summary>
  
베이스라인은 질의응답만 할 수 있을 뿐 챗봇이 아닙니다. 대화형 Q & A는 할 수 없습니다. 대화형 Q & A를 구현해보는건 어떨까요? (e.g. [Mendable](https://www.mendable.ai))

</details>

### Multimodal Q & A

<details>
  <summary> 펼치기 </summary>
  
베이스라인은 텍스트만 이해합니다. 이미지로 증강할 수는 없을까요? 멀티모달 정보로 증강을 해보는건 어떨까요?  (e.g. [GPT4의 위력](https://www.clien.net/service/board/park/17962934), Bard Lens)

</details>

### Real-time Q & A

<details>
  <summary> 펼치기 </summary>

베이스라인처럼 검색엔진을 직접 구축할 필요가 있을까요?  그냥 구글을 쓰면 되지 않을까요? 실시간 정보도 얻을 수 있지 않을까요? Retreiver를 구글 검색으로 바꿔보는건 어떨까요? (e.g. [WebChatGPT](https://chrome.google.com/webstore/detail/webchatgpt-chatgpt-with-i/lpfemeioodjbpieminkklglpmhlngfcn))

</details>


