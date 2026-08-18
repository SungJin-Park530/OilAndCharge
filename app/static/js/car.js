document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('carModal');
    const openBtn = document.getElementById('openModalBtn');
    const closeBtn = document.getElementById('closeModalBtn');
    const cancelBtn = document.getElementById('cancelModalBtn');
    const form = document.getElementById('carRegisterForm');

    // 요소들이 제대로 잡혔는지 확인 (F12 콘솔창에서 확인 가능)
    console.log('modal:', modal);
    console.log('openBtn:', openBtn);

    if (!openBtn || !modal) {
        console.error('필수 요소를 찾지 못했습니다!');
        return;
    }

    // 차량 등록 클릭 시 모달 창 열기 + 입력 폼 초기화
    openBtn.addEventListener('click', () => {
        form.reset();
        modal.classList.add('active');
    });

    // 모달 창 닫기 함수
    function closeModal() {
        modal.classList.remove('active');
        form.reset();
    }

    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (cancelBtn) cancelBtn.addEventListener('click', closeModal);

    // 모달 바깥 영역 클릭 시 닫기
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });
});