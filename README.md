

<p align="center">
  <img width="400" height="218" alt="reborn_logo" src="https://github.com/user-attachments/assets/fb0fddfa-531a-413c-bc07-8e5e7f9b0875" />
</p>

# REBORN
> **중고상품 거래 플랫폼** <br>
Flask 프레임워크 기반으로 제작된 웹 애플리케이션 REBORN 입니다.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white">
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white">
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black">
  
  <br>
  
  <img src="https://img.shields.io/badge/Bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white">
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white">
  <img src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white">
</p>

---

## 프로젝트 기간

2026.04.03 ~ 2026.04.29

---

## 팀 구성
| 이름  | 담당 영역                                    | 
| --- | ---------------------------------------------- |
| 임승찬 | 프로젝트 총괄 / 메인페이지 / 구조 설계 / 최적화 |   
| 심세은 | 로그인 / 회원가입 / 인증 시스템                | 
| 서창환 | 상품 상세 / 댓글 / 찜 기능                    | 
| 성정훈 | 마이페이지 / 거래내역 / 리뷰 시스템            | 

---

## 프로젝트 소개

>REBORN(리본)은 사용자 간 중고 물품을 거래할 수 있도록 제작된 웹 플랫폼입니다.<br>
단순 상품 게시판이 아닌 실제 거래 흐름을 고려하여 다음 기능을 구현하였습니다.

* 마이페이지 / 거래내역 관리
* 판매자 프로필
* 찜 기능
* 거래 완료 처리 및 거래 후기
* 상품 문의 댓글 시스템

---

## 기술 스택

| 구분         | 사용 기술                                                                  |
| ---------- | ---------------------------------------------------------------------- |
| Frontend   | HTML5, CSS3, JavaScript, BOOTSTRAP, Jinja2                             |
| Backend    | Python, Flask                                                          |
| Database   | SQLAlchemy (Flask PKG)                                                 |
| Deployment | Docker                                                                 |

---

## 프로젝트 구조
```bash id="5w4k5p"
project/
├── .venv/                      # 파이썬 가상환경
├── market/                     # 메인 애플리케이션 패키지
│   ├── static/                 # 정적 파일 (CSS, JS, 이미지)
│   │   ├── img/                # 시스템 기본 이미지 및 아이콘
│   │   ├── script/             # 자바스크립트 파일 (app.js 등)
│   │   ├── style/              # 페이지별 CSS 파일 (login.css, main.css 등)
│   │   └── uploads/            # 사용자 업로드 파일 관리
│   │       ├── products/       # 등록된 상품 이미지 저장
│   │       └── profiles/       # 사용자 프로필 이미지 저장
│   ├── templates/              # HTML 템플릿 파일
│   │   ├── auth/               # 인증 관련 (login.html, signup.html 등)
│   │   ├── items/              # 상품 관련 (item_list.html, PDP.html 등)
│   │   ├── personal/           # 개인화 및 공통 레이아웃 (base.html, header.html 등)
│   │   └── main.html           # 메인 페이지
│   ├── views/                  # Flask Blueprint 비즈니스 로직
│   │   ├── auth_view.py        # 로그인/회원가입 로직
│   │   ├── main_view.py        # 메인 화면 로직
│   │   ├── mypage_view.py      # 마이페이지 관련 로직
│   │   ├── product_view.py     # 상품 등록/상세 로직
│   │   └── review_view.py      # 리뷰 작성 및 관리 로직
│   ├── __init__.py             # 앱 초기화 및 Blueprint 등록
│   ├── filter.py               # 템플릿 커스텀 필터
│   ├── forms.py                # Flask-WTF 폼 정의
│   ├── models.py               # SQLAlchemy 데이터베이스 모델링
│   └── footer_content.py       # 하단 정보 관리 로직
├── migrations/                 # 데이터베이스 마이그레이션 이력
├── .env                        # 환경 변수 설정 파일 (비밀키, DB 주소 등)
├── .gitignore                  # Git 제외 대상 설정
├── config.py                   # Flask 앱 환경 설정
├── Dockerfile                  # 도커 배포 설정
├── seed.py                     # 초기 마스터 데이터 주입 스크립트
├── market.db                   # SQLite 데이터베이스 파일
├── README.md                   # 프로젝트 개요 및 매뉴얼
└── requirements.txt            # 설치된 패키지 목록

```
---

## 데이터베이스 구조

### 주요 테이블

User / Item / ItemImage / Category / ItemStatus / Favorite / Deal / Review / Comment

<details>
<summary>Entity 정의</summary>
<br>
  
* 사용자(User): 서비스 이용 주체로, 상품 판매·구매 및 커뮤니티 활동을 수행합니다.
* 상품(Item): 거래의 대상이 되는 실물 객체이며, 특정 카테고리와 판매 상태를 가집니다.
* 상품 상태(ItemStatus): '판매 중', '예약 중', '판매 완료' 등 상품의 현재 단계를 관리합니다.
* 카테고리(Category): 상품을 논리적으로 분류하는 체계입니다.
* 거래(Deal): 판매자와 구매자 간의 매매 계약 성립을 기록하며, 가격과 일시를 포함합니다.
* 리뷰(Review): 완료된 거래를 기반으로 작성되는 서비스 피드백 기록입니다.
* 댓글(Comment): 상품에 대한 질의응답 및 대화 기록으로, 계층형 대댓글 구조를 지원합니다.
* 찜하기(Favorite): 사용자가 관심 있는 상품을 보관하는 논리적 연결 객체입니다.
* 상품 이미지(ItemImage): 상품 상세 설명을 위한 미디어 파일 경로를 관리합니다.

</details>

핵심 관계

* User 1:N Item (회원은 여러 상품 등록 가능)
* User N:M Item (찜 기능 → Favorite 테이블 사용)
* Item 1:N Comment (상품 문의 댓글)
* Deal 1:1 Review (거래 완료 후 리뷰 작성)
* User 1:N Review (판매자가 여러 리뷰 수신 가능)
* Comment 1:N Comment (자기 참조 계층형 구조로 하나의 댓글(부모)은 여러 개의 답글(자식)을 가질 수 있음)
---
## 주요 기능

<details>
<summary>기능 목록 보기</summary>

### 회원 기능

* 회원가입
* 로그인 / 로그아웃
* 카카오 로그인
* 아이디 찾기
* 비밀번호 재설정
* 로그인 세션 유지
* 회원정보 수정
* 프로필 이미지 변경
* 상태 메시지 설정

### 상품 기능

* 상품 등록 / 수정 / 삭제
* 상품 이미지 다중 업로드
* 상품 상세 페이지
* 카테고리별 조회
* 검색 기능
* 판매 상태 관리<br>

  ⌞ 판매 상태: 판매중 / 예약중 / 판매완료

### 마이페이지 기능

* 판매 중 상품 조회
* 찜 목록 조회
* 받은 리뷰 조회
* 거래 내역 이동
* 프로필 관리

### 찜 기능

* 상품 찜 등록 / 해제
* 찜 개수 표시
* 마이페이지 찜 목록 조회

### 거래 기능

* 판매완료 처리
* 거래 상대 등록
* 구매 이력 조회
* 판매 내역 조회
* 삭제 상품 거래 기록 유지

### 리뷰 기능

* 거래 완료 지정된 사용자만 리뷰 작성 가능
* 거래당 1회 리뷰 작성 제한
* 받은 리뷰 조회

### 댓글 / 문의 기능

* 상품 문의 댓글 작성
* 판매자 답변 기능
* 대댓글 구조
* 비밀 댓글 기능

</details>

---

## 주요 화면

<details>
<summary>스크린샷 보기</summary>

<br>

### 1. 인트로 페이지

<img width="791" height="674" alt="image" src="https://github.com/user-attachments/assets/f36076f8-47db-4596-8bc5-5fdb288e949f" />

<br><br>

### 2. 로그인 / 회원가입

* 일반 로그인과 카카오 로그인을 지원합니다.

<img width="803" height="512" alt="image" src="https://github.com/user-attachments/assets/02221595-4cf7-42bd-93e8-1ae6fdc1226f" />

<br><br>

* 실시간 중복 검사 및 입력 검증 기능을 제공합니다.

<img width="946" height="758" alt="image" src="https://github.com/user-attachments/assets/cebd4224-e6f1-41df-883d-0ff694c5512a" />

<br><br>

### 3. 메인 페이지

* 최신 등록 상품 순으로 출력됩니다.
* 카테고리 / 검색 / 판매중 필터 제공합니다.

<img width="1900" height="2913" alt="main" src="https://github.com/user-attachments/assets/a9e59675-0673-4094-8c5f-024148afe9cb" />

<br><br>

<img width="1920" height="952" alt="category" src="https://github.com/user-attachments/assets/cf870c72-5a0a-4aee-aefa-31cca90bd4f5" />
카테고리 선택

<br><br>

<img width="1920" height="952" alt="filter" src="https://github.com/user-attachments/assets/2d41127b-6127-4539-807f-88e636a23ffd" />
판매중인 상품만 보기 필터링

<br><br>

### 4. 상품 등록
* 상품 이미지 업로드 및 카테고리 선택이 가능합니다.
* 입력값 검증과 빈칸 안내 기능을 제공합니다.
<img width="851" height="788" alt="image" src="https://github.com/user-attachments/assets/1a84cc55-ee48-4537-95cf-f2206a77e3c2" />

<br><br>

### 5. 상품 상세

* 판매자가 직접 상품 상태를 변경하고 게시글을 관리합니다.

<img width="793" height="488" alt="판매자 사진" src="https://github.com/user-attachments/assets/030c739a-1cf8-4d8e-8bd6-1592435ebd73" />


<br><br>

### 6. 상품 문의 / 댓글
* 비밀댓글을 활용한 문의하기가 가능합니다.

<img width="627" height="835" alt="1234" src="https://github.com/user-attachments/assets/8114b35c-6d04-4f88-acc6-98a0ef5f4a4d" />
 <br><br>

 
* **제 3자에게는 보이지 않습니다.**

<br><br>
  <img width="648" height="170" alt="기능2" src="https://github.com/user-attachments/assets/10199e92-c1b6-4a5c-8730-4aab52e29415" />
  
<br><br>

<img width="1920" height="952" alt="comment" src="https://github.com/user-attachments/assets/56789ae8-58c9-4f7e-a56c-c832d32018d3" />
댓글달기





<br><br>

### 7. 거래 완료 / 구매자 등록
* 판매완료 처리 후 거래 상대를 등록할 수 있습니다.
* 등록된 거래 정보는 리뷰 시스템과 연동됩니다.
<img width="1007" height="553" alt="거래완료" src="https://github.com/user-attachments/assets/3f97b53c-02fc-4638-852e-3a14648db718" />


<br>

### 8. 마이페이지
* 판매 상품, 찜 목록, 받은 리뷰를 한 곳에서 관리할 수 있습니다.
* 프로필 이미지 및 상태 메시지 수정 기능을 제공합니다.

<br>

<img width="876" height="823" alt="마이페이지" src="https://github.com/user-attachments/assets/2ab3c84d-8653-4b6c-bcbf-e0d08ba864bc" />
<br><br>

<img width="1920" height="952" alt="mypage" src="https://github.com/user-attachments/assets/edaaf26c-de53-4ff6-9c34-3b532ff293df" />
마이페이지

<br><br>

### 9. 거래 내역

<img width="871" height="437" alt="거래" src="https://github.com/user-attachments/assets/994486a2-1b76-4cf9-98c9-449ffdc10edc" />


<br><br>

### 10. 리뷰 기능
* 거래 한 건당 한 번의 리뷰만 작성 가능합니다.
<img width="882" height="581" alt="5" src="https://github.com/user-attachments/assets/fb1c1bf6-89df-4561-8ed7-20cf927eb3b6" />

<br><br>

<img width="1920" height="952" alt="review" src="https://github.com/user-attachments/assets/6fc768bd-d3bb-4099-918f-3f9dd9c8ee03" />
리뷰작성

<br><br>

</details>

---

## 역할 분담

<details>
<summary>상세 역할 보기</summary>

### 임승찬

* 프로젝트 전체 구조 설계 (DB 구조, 시스템 설계)
* 메인 페이지 / 카테고리 페이지 / 키워드 검색 페이지 구현
* 각 페이지 프로토타입 디자인 설계
* 페이지네이션 및 성능 최적화
* 공용 CSS / JS 구조 통합
* 이미지 업로드 구조 개선

### 심세은

* 로그인 / 회원가입 기능 구현
* 카카오 로그인 연동
* 계정 찾기 / 비밀번호 재설정
* 실시간 중복 검사
* 회원 인증 UX 개선

### 서창환

* 상품 상세 페이지 구현
* 댓글 / 문의 / 판매자 답변 기능
* 비밀 댓글 기능
* 찜 기능 및 UI 개선

### 성정훈

* 마이페이지, 판매자 프로필 페이지 구현
* 프로필 이미지 기능 구현
* 리뷰 시스템 구현
* 거래 내역 시스템 구현

</details>

---

## Docker 설치 환경에서 실행 방법
<details>
  <summary>실행 명령어 확인</summary>
  
### 1. 이미지 다운로드
```bash
docker pull seungchan1122/reborn:v1
```

### 2. 컨테이너 실행
* 내부포트 5000, 외부포트 5000

```bash
docker run -d -p 5000:5000 --name reborn-container seungchan1122/reborn:v1
```

### 3. 컨테이너 관련 CMD
이미지 조회
```bash
docker images
```

오프라인 상태의 컨테이너까지 조회 (-a 옵션)
```bash
docker ps -a
```

컨테이너 중지
```bash
docker stop reborn-container
```

컨테이너 재실행
```bash
docker start reborn-container
```
</details>

---
## 트러블 슈팅

<details>
<summary>해결 사례 보기</summary>

### 1. 이미지 경로 문제

* 업로드 이미지가 출력되지 않는 문제 발생
* 사용자별 디렉토리 구조 재설계로 해결

### 2. 삭제된 상품 거래기록 문제

* 게시글 삭제 시 거래내역 손실 문제 발생
* Soft Delete 방식으로 개선

### 3. 탭 유지 문제

* 새로고침 시 탭 초기화 문제 발생
* Query Parameter + JavaScript 방식으로 해결

### 4. 리뷰 기능 문제
* 구매자와 판매자를 특정하는 데이터 테이블이 없어 리뷰 기능을 구현할 수 없는 문제 발생
* 판매완료로 상태변경시 구매자의 닉네임을 등록하는 방식으로 해결

</details>

---

## 프로젝트 회고
<details>
<summary>팀원 회고 보기</summary>

### 임승찬

이번 프로젝트에서 팀장의 역할을 맡아 전반적인 구조 및 시스템 설계, 백엔드 개발을 총괄했습니다.

팀장 역할과 협업, Flask와 DB를 활용한 웹개발은 처음이라 도전자의 자세로 프로젝트를 진행했습니다.

개발 중 변수 관리 미흡으로 인한 에러를 겪으며 단순히 기능 구현만 한다는 목표가 아닌 팀원 간 프로젝트 내 규격 공유, 실시간 소통, 피드백이 협업 프로젝트의 완성도를 높인다는 것을 깨달았습니다.

새로운 기술을 배웠다는 것뿐만 아니라 팀원들과의 소통을 통해 개발 중 일어난 문제 현상을 극복하고 서비스를 완성해 나가는 협업의 가치를 배운 계기가 되었습니다.


<br>

### 심세은

Flask 기반 중고거래 프로젝트를 통해 효율적인 데이터베이스 설계와 안정적인 시스템 운영의 중요성을 깊이 체감했습니다.

특히 팀원들과 git organization을적극 활용하며 지속적으로 소통한 덕분에 문제 해결 능력을 키울 수 있었고, 문서화 작업까지 체계적으로 마무리하며 프로젝트 관리 역량도 한층 강화되었습니다.

<br>

### 서창환

Flask 프로젝트가 처음이라 생소했지만,  프론트엔드의 기초인 HTML, CSS , JS 부터 차근차근 다지며 완성도를 높였습니다.

특히 제가 맡은 상품 상세페이지와 문의 시스템을 담당하며 마주한 기술적 난관들을 팀원들과의 활발한 소통으로 해결하며 협업의 가치를 깊이 배운 계기가 되었습니다.

<br>

### 성정훈

Flask와 웹 개발이 처음이어서 초반에는 프로젝트 구조를 이해하고 팀 개발 흐름에 적응하는 과정이 쉽지 않았습니다.

초기에는 거래 상태 변경 로직이 어렵다고 판단해 생략했지만, 프로젝트 중반에 리뷰 기능을 구현하려 하니 구매자와 판매자를 특정할 수 없는 문제가 발생했습니다. 

기존 기능을 크게 수정하지 않는 방향으로 고민한 끝에, 판매완료 시 거래자를 등록하여 판매자·구매자·상품 정보를 연결하는 거래 테이블 구조를 활용해 리뷰 시스템을 구현할 수 있었습니다.

이번 프로젝트를 통해 기술적인 성장뿐 아니라 문제 해결 과정의 중요성과 협업 경험의 가치를 배울 수 있었습니다.

<br>

</details>

---

## GitHub Repository

https://github.com/project-flask/flask_project
