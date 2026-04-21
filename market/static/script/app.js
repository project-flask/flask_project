document.addEventListener('DOMContentLoaded', function () {

    // toast 모든 페이지 기능 공유
    const toastList = ['saveToast', 'logoutToast'];
    toastList.forEach(id => {
        const toast = document.getElementById(id);
        if (toast) {
            if (toast.classList.contains('toast') && typeof bootstrap !== 'undefined') {
                const bsToast = new bootstrap.Toast(toast, { autohide: false });
                bsToast.show();
            }
            setTimeout(function () {
                toast.style.opacity = '0';
                setTimeout(() => { if (toast.parentNode) toast.remove(); }, 500);
            }, 1500);
        }
    });

    // 상단 header 고정 ( header.html )
    const headerFixed = document.querySelector('.hfixed');
    if (headerFixed) {
        const navHeight = headerFixed.offsetHeight;
        window.addEventListener('scroll', function () {
            if (window.scrollY >= 40) {
                headerFixed.classList.add('active');
                document.body.style.paddingTop = navHeight + 'px';
            } else {
                headerFixed.classList.remove('active');
                document.body.style.paddingTop = '0';
            }
        });
    }

    // 하단 footer 리스트 모달 팝업 ( footer.html )
    const openBtns = document.querySelectorAll('.modal_open_btn');
    const closeBtns = document.querySelectorAll('.modal_close_btn');

    openBtns.forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = 'modal_' + this.getAttribute('data-target');
            const targetModal = document.getElementById(targetId);
            if (targetModal) {
                targetModal.style.backgroundColor = 'rgba(0, 0, 0, 0.3)';
                targetModal.style.display = 'flex';
                document.body.style.overflow = 'hidden';
            }
        });
    });

    closeBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            const modal = this.closest('.modal_style_pkg');
            if (modal) {
                modal.style.display = 'none';
                document.body.style.overflow = 'auto';
            }
        });
    });

    // 계정/인증 구간 (로그인, 회원가입, 계정찾기, 재설정)

    // 계정찾기 탭, 오토포커스 기능
    const findContainer = document.getElementById('find-container');
    if (findContainer) {
        const idTabBtn = document.getElementById('id-tab');
        const pwTabBtn = document.getElementById('pw-tab');
        const isPwError = findContainer.getAttribute('data-is-pw-error') === 'true';

        function setFocus(selector) {
            setTimeout(() => {
                const input = document.querySelector(selector);
                if (input) input.focus();
            }, 0);
        }

        if (isPwError && pwTabBtn && typeof bootstrap !== 'undefined') {
            const pwTab = new bootstrap.Tab(pwTabBtn);
            pwTab.show();
            setFocus('#find-pw input[name="user_id"]');
        } else {
            setFocus('#find-id input[name="username"]');
        }

        function clearFindData() {
            document.querySelectorAll('.custom-input').forEach(input => input.value = '');
            document.querySelectorAll('.alert').forEach(alert => alert.remove());
        }

        if (idTabBtn) idTabBtn.addEventListener('shown.bs.tab', () => { clearFindData(); setFocus('#find-id input[name="username"]'); });
        if (pwTabBtn) pwTabBtn.addEventListener('shown.bs.tab', () => { clearFindData(); setFocus('#find-pw input[name="user_id"]'); });
    }

    // 비밀번호 보이기/숨기기 토글 ( 통합 경량화 )
    const pwToggles = document.querySelectorAll('.toggle-pw, #togglePassword');
    pwToggles.forEach(icon => {
        icon.addEventListener('click', function () {
            const targetId = this.getAttribute('data-target') || 'login-password';
            const passwordInput = document.getElementById(targetId);
            if (passwordInput) {
                const isPassword = passwordInput.getAttribute('type') === 'password';
                passwordInput.setAttribute('type', isPassword ? 'text' : 'password');
                this.classList.toggle('bi-eye');
                this.classList.toggle('bi-eye-slash');
            }
        });
    });

    // 보안 강도 체크 ( 통합 경량화 )
    const strengthConfigs = [
        { input: 'signup-pw1', bar: 'strength-bar', text: 'strength-text' },
        { input: 'reset-pw1', bar: 'strength-bar-reset', text: 'strength-text-reset' }
    ];

    strengthConfigs.forEach(conf => {
        const pwInput = document.getElementById(conf.input);
        const strengthBar = document.getElementById(conf.bar);
        const strengthText = document.getElementById(conf.text);

        if (pwInput && strengthBar && strengthText) {
            pwInput.addEventListener('input', function () {
                const val = pwInput.value;
                if (val.length === 0) { updateUI(strengthBar, strengthText, '0%', '#999', '보안 강도'); return; }

                const hasLetter = /[a-zA-Z]/.test(val), hasNumber = /[0-9]/.test(val), hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(val);
                const len = val.length;

                if (hasLetter && hasNumber && hasSpecial && len >= 8) updateUI(strengthBar, strengthText, '100%', '#CCCCFF', '높음 (안전한 비밀번호입니다)');
                else if (hasLetter && hasNumber && len >= 6) updateUI(strengthBar, strengthText, '66%', '#ffcc00', '보통 (특수문자를 섞어보세요)');
                else updateUI(strengthBar, strengthText, '33%', '#ff6b6b', '낮음 (보안이 약해요)');
            });
        }
    });

    function updateUI(bar, txt, width, color, msg) {
        if (bar && txt) {
            bar.style.width = width; bar.style.backgroundColor = color;
            txt.innerText = msg; txt.style.color = color;
        }
    }

    // JS: 화면 전환 / 회원가입 중복 체크 ( 아이디, 닉네임, 이메일 ) / 이메일 도메인 추천 (( singup.html )
    // [화면 전환(이메일로 시작하기 - 이메일 회원가입)]
    window.toggleForm = function() {
        const selectArea = document.getElementById('select-area');
        const formArea = document.getElementById('email-form-area');
        const title = document.getElementById('signup-title');
        const card = document.querySelector('.signup-card-custom');
        if (!selectArea || !formArea || !card) return;

        // 폼이 닫혀있다가 열릴 때 (이메일 입력 화면)
        if (formArea.style.display === 'none' || formArea.style.display === '') {
            selectArea.style.display = 'none';
            formArea.style.display = 'block';
            card.style.setProperty('max-width', '1050px', 'important');
            const inp = document.querySelector('input[name="user_id"]');
            if(inp) inp.focus();
        }

        // 폼이 열려있다가 닫힐 때 (선택 화면으로 돌아갈 때)
        else {
            selectArea.style.display = 'block';
            formArea.style.display = 'none';
            card.style.setProperty('max-width', '850px', 'important');
        }
    };

    // 서버 에러 발생 시 자동으로 폼 열어주기
    const signupContainer = document.getElementById('signup-container');
    if (signupContainer && signupContainer.getAttribute('data-has-errors') === 'true')
        window.toggleForm();

    // 중복 체크 함수 ( 아이디, 닉네임, 이메일 ), 글자 수 체크
    function checkDuplicate(inputId, msgId, url, dataKey) {
        const inputElement = document.getElementById(inputId);
        if (!inputElement) return;

        // 사용자가 다시 타이핑하면
        inputElement.addEventListener('input', function () {
            // 1. form.py 에러 메시지 제거
            const parent = inputElement.closest('.mb-3') || inputElement.closest('.mb-4');
        if (parent) {
            parent.querySelectorAll('.invalid-feedback-custom').forEach(err => err.remove());
        }

            // 2. 입력창 빨간 테두리 제거
            inputElement.classList.remove('is-invalid');

            // 3. 서버 에러 시 사라졌던 메시지창이 없으면 새로 생성
            let msgElement = document.getElementById(msgId);

            if (!msgElement) {
                const newDiv = document.createElement('div');
                newDiv.id = msgId;
                newDiv.className = "check-msg";
                inputElement.after(newDiv);
            }
            else {
                msgElement.innerText = "";
            }
        });

        // 입력 완료 -> 포커스 나갈 때 중복 체크 실행
        inputElement.addEventListener('blur', function() {
            const value = inputElement.value.trim();
            if (value === "") return;

        // 아이디, 닉네임 글자 수 검증(
            let minLen = 0;
            let maxLen = 0;
            let label = "";

            if (dataKey === 'user_id') {
                minLen = 3; maxLen = 20; label = "아이디";
            }
            else if (dataKey === 'nickname') {
                minLen = 2; maxLen = 10; label = "닉네임";
            }

            // 글자 수 조건이 있는 경우(아이디, 닉네임) 먼저 체크
            if (minLen > 0 && (value.length < minLen || value.length > maxLen)) {
                const msgElement = document.getElementById(msgId);
                if (msgElement) {
                    msgElement.innerText = `${label}는 ${minLen}~${maxLen}자여야 합니다.`;
                    msgElement.style.color = "#dc3545";
                }
                inputElement.classList.add('is-invalid');
                return;
            }

            fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ [dataKey]: value })
            }).then(res => res.json()).then(data => {
                msgElement = document.getElementById(msgId);
                if (!msgElement) return;

                // 중복된 경우
                if (data.exists) {
                    msgElement.innerText = "이미 사용 중입니다.";
                    msgElement.style.color = "#dc3545";
                    inputElement.classList.add('is-invalid');
                // 사용 가능한 경우
                } else {
                    msgElement.innerText = "사용 가능합니다!";
                    msgElement.style.color = "#9C96F3";
                    inputElement.classList.remove('is-invalid');
                }
            });
        });
    }

    // 아이디, 닉네임, 이메일 각각 실행(4/21 추가)
checkDuplicate('user_id', 'id-check-msg', "/auth/check_id_duplicate/", 'user_id');
checkDuplicate('nickname', 'nickname-check-msg', "/auth/check_nickname_duplicate/", 'nickname');
checkDuplicate('email', 'email-check-msg', "/auth/check_email_duplicate/", 'email');
checkDuplicate('phone', 'phone-check-msg', "/auth/check_phone_duplicate/", 'phone');
checkDuplicate('username', null, null, 'username');
checkDuplicate('signup-pw1', null, null, 'password1');
checkDuplicate('signup-pw2', null, null, 'password2');
checkDuplicate('login-password', null, null, 'password');

    // [이메일 도메인 자동 추천 JS (4/17)]
    const emailInput = document.getElementById('email');
    const emailDataList = document.getElementById('email-options');
    const domains = ['naver.com', 'gmail.com', 'kakao.com', 'daum.net', 'hanmail.net', 'outlook.com'];

    if (emailInput && emailDataList) {
        emailInput.addEventListener('input', function() {
            const value = this.value;

            // '@'가 포함되었을 때 추천 도메인 보이게
            if (value.includes('@')) {
                const [userPart, domainPart] = value.split('@');
                emailDataList.innerHTML = ''; // 이전 목록 초기화

                domains.forEach(domain => {
                    const option = document.createElement('option');
                    // 사용자가 입력한 아이디 부분 + 추천 도메인
                    option.value = `${userPart}@${domain}`;
                    emailDataList.appendChild(option);
                });
            }
        });
    }

    // 판매 중만 보기 필터링 ( main.html, CP.html 공용 )
    const sellOnlyCheck = document.getElementById('sellOnlyCheck');
    if (sellOnlyCheck) {
        sellOnlyCheck.addEventListener('change', function () {
            const isChecked = this.checked;
            document.querySelectorAll('.product-item').forEach(item => {
                item.style.display = (isChecked && item.getAttribute('data-status') !== '1') ? 'none' : 'block';
            });
        });
    }

    // 상품 이미지 페이지네이션 기능, 상품 삭제 시 alert ( PDP.html ) 4월20일 코드 수정
    const slides = document.querySelectorAll('.p-detail-img');
    const slideNum = document.getElementById('slideNum');
    let slideIdx = 0;

    window.moveSlide = function (n) {
        if (slides.length <= 1) return;
        slides[slideIdx].style.display = 'none';
        slideIdx = (slideIdx + n + slides.length) % slides.length;
        slides[slideIdx].style.display = 'block';
        if (slideNum) slideNum.innerText = slideIdx + 1;
    };

    window.handleInquiryClick = function(){
        const form = document.getElementById('comment-form');
        const contentInput = document.getElementById('content');

        if (form && contentInput) {
            form.style.display = 'block';
            form.scrollIntoView({ behavior: 'smooth', block: 'center' });
            contentInput.focus();
        }
    };

    // 게시글 삭제 컨펌 함수 (직접 호출 방식으로 변경하여 중복 방지)
    window.confirmDelete = function (deleteUrl) {
        if (confirm("정말로 삭제하시겠습니까? 다시 되돌릴 수 없습니다.")) {
            location.href = deleteUrl;
        }
    };

    // 댓글 더 보기 기능
    window.showAllComments = function () {
        // 1. 숨겨진 모든 댓글 요소를 가져옵니다.
        const comments = document.querySelectorAll('.comment-item');

        // 2. 모든 댓글을 보이게 바꿉니다.
        comments.forEach(item => {
            item.style.display = 'block';
        });

        // 3. 더 보기 버튼은 더 이상 필요 없으므로 숨깁니다.
        const btn = document.getElementById('load-more-btn');
        if (btn) {
            btn.style.display = 'none';
        }
    };

    // 상품 업로드 페이지 사진 업로드 구간 기능 ( write.html )
    const input = document.getElementById('images-input');
    const container = document.getElementById('preview-container');
    let selectedFiles = [];

    if (input && container) {
        input.addEventListener('change', e => {
            selectedFiles = [...selectedFiles, ...Array.from(e.target.files)].slice(0, 10);
            render();
        });

        window.remove = function (i) {
            selectedFiles.splice(i, 1);
            const dt = new DataTransfer(); selectedFiles.forEach(f => dt.items.add(f));
            input.files = dt.files; render();
        };

        function render() {
            container.innerHTML = '';
            if (selectedFiles.length === 0) { fillEmptySlots(); return; }
            selectedFiles.forEach((file, i) => {
                const reader = new FileReader();
                reader.onload = e => {
                    const div = document.createElement('div'); div.className = 'preview-item';
                    div.innerHTML = `<img src="${e.target.result}"><button type="button" class="btn-remove" onclick="remove(${i})">×</button>
                        ${i === 0 ? '<div style="position:absolute; bottom:0; width:100%; background:rgba(204,204,255,0.8); color:white; font-size:10px; text-align:center;">메인 이미지</div>' : ''}`;
                    container.appendChild(div);
                    if (i === selectedFiles.length - 1)
                        fillEmptySlots();
                };
                reader.readAsDataURL(file);
            });
        }

        function fillEmptySlots() {
            const currentCount = container.querySelectorAll('.preview-item').length;
            for (let i = currentCount; i < 9; i++) {
                const empty = document.createElement('div');
                empty.className = 'preview-item empty-slot';
                empty.innerHTML = '<i class="fas fa-plus"></i>';
                container.appendChild(empty);
            }
        }
        fillEmptySlots();
    }

    // 마이페이지, 판매자페이지 ( mypage.html, seller_profile.html )
    window.initSlider = function (trackId, prevBtnId, nextBtnId) {
        const track = document.getElementById(trackId), prevBtn = document.getElementById(prevBtnId), nextBtn = document.getElementById(nextBtnId);
        if (!track || !prevBtn || !nextBtn) return;
        const slidesItems = track.querySelectorAll('.product-slide');
        if (!slidesItems.length) return;
        let currentIndex = 0;

        const updateSlider = () => {
            const visibleCount = window.innerWidth <= 767 ? 1 : (window.innerWidth <= 991 ? 2 : 4);
            const maxIndex = Math.max(0, slidesItems.length - visibleCount);
            currentIndex = Math.min(currentIndex, maxIndex);
            track.style.transform = `translateX(-${currentIndex * (slidesItems[0].offsetWidth + 16)}px)`;
            prevBtn.disabled = (currentIndex === 0); nextBtn.disabled = (currentIndex >= maxIndex);
        };

        prevBtn.onclick = () => { currentIndex = Math.max(0, currentIndex - 1); updateSlider(); };
        nextBtn.onclick = () => { currentIndex++; updateSlider(); };
        window.addEventListener('resize', updateSlider); updateSlider();
    };

    // 슬라이더 실행
    initSlider('productSliderTrack', 'productPrevBtn', 'productNextBtn');
    initSlider('wishSliderTrack', 'wishPrevBtn', 'wishNextBtn');
    initSlider('sellerProductSliderTrack', 'sellerProductPrevBtn', 'sellerProductNextBtn');

    // 리뷰 더보기 및 상태메시지
    const toggleBtn = document.getElementById('toggleReviewBtn');
    if (toggleBtn) {
        let expanded = false;
        toggleBtn.onclick = () => {
            document.querySelectorAll('.review-hidden').forEach(r => r.style.display = expanded ? 'none' : 'flex');
            expanded = !expanded; toggleBtn.textContent = expanded ? '접기' : '더보기';
        };
    }

    const editBtn = document.getElementById('statusEditBtn');
    if (editBtn) {
        const viewMode = document.getElementById('statusViewMode'), editMode = document.getElementById('statusEditMode');
        const statusInput = document.getElementById('statusInput'), statusText = document.getElementById('statusText');
        editBtn.onclick = () => {
            statusInput.value = statusText.textContent.trim() === "상태 메시지를 입력하세요" ? "" : statusText.textContent.trim();
            viewMode.style.display = 'none'; editMode.style.display = 'block'; editBtn.style.display = 'none'; statusInput.focus();
        };
        const cancelBtn = document.getElementById('statusCancelBtn');
        if (cancelBtn) cancelBtn.onclick = () => { editMode.style.display = 'none'; viewMode.style.display = 'block'; editBtn.style.display = 'inline-block'; };
    }
});