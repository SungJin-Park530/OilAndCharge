document.addEventListener(
    'DOMContentLoaded',
    function () {

        // =====================================
        // DOM 요소
        // =====================================

        const modal =
            document.getElementById(
                'carModal'
            );

        const openBtn =
            document.getElementById(
                'openModalBtn'
            );

        const closeBtn =
            document.getElementById(
                'closeModalBtn'
            );

        const cancelBtn =
            document.getElementById(
                'cancelModalBtn'
            );

        const form =
            document.getElementById(
                'carRegisterForm'
            );

        const vehicleList =
            document.getElementById(
                'vehicle-list'
            );


        // =====================================
        // 차량 등록 모달 열기
        // =====================================

        openBtn.addEventListener(
            'click',
            function () {

                // 이전 입력값 초기화
                form.reset();

                // 모달 표시
                modal.classList.add(
                    'active'
                );
            }
        );


        // =====================================
        // 차량 등록 모달 닫기
        // =====================================

        function closeModal() {

            modal.classList.remove(
                'active'
            );

            form.reset();
        }


        if (closeBtn) {

            closeBtn.addEventListener(
                'click',
                closeModal
            );
        }


        if (cancelBtn) {

            cancelBtn.addEventListener(
                'click',
                closeModal
            );
        }


        // 모달 바깥 영역 클릭 시 닫기
        modal.addEventListener(
            'click',
            function (event) {

                if (event.target === modal) {
                    closeModal();
                }
            }
        );


        // =====================================
        // DB 차량 목록 조회
        // =====================================

        async function loadVehicles() {

            vehicleList.innerHTML =
                '<p>차량 정보를 불러오는 중...</p>';

            try {

                // Flask 차량 조회 API 호출
                const response =
                    await fetch(
                        '/api/vehicles'
                    );

                const data =
                    await response.json();


                if (!response.ok) {

                    throw new Error(
                        data.error ||
                        '차량 목록 조회에 실패했습니다.'
                    );
                }


                // 조회된 차량을 화면에 출력
                renderVehicles(
                    data.vehicles
                );


            } catch (error) {

                console.error(
                    '차량 목록 조회 오류:',
                    error
                );

                vehicleList.innerHTML =
                    '<p>차량 정보를 불러오지 못했습니다.</p>';
            }
        }


        // =====================================
        // 차량 목록 화면 출력
        // =====================================

        function renderVehicles(
            vehicles
        ) {

            vehicleList.innerHTML = '';


            // 등록 차량이 없는 경우
            if (
                !vehicles ||
                vehicles.length === 0
            ) {

                vehicleList.innerHTML =
                    '<p>등록된 차량이 없습니다.</p>';

                return;
            }


            vehicles.forEach(
                function (vehicle) {

                    const card =
                        document.createElement(
                            'div'
                        );


                    card.className =
                        'station-card';


                    card.innerHTML = `
                        <div class="station-header">

                            <span class="station-name">
                                ${vehicle.vehicle_name}
                            </span>

                            <span
                                class="badge-optimal"
                                style="background-color:#4b5563;"
                            >
                                ${vehicle.fuel_type}
                            </span>

                        </div>


                        <div class="car-card-body">

                            <div class="car-info-row">

                                <span class="car-info-label">
                                    소유주
                                </span>

                                <span class="car-info-value">
                                    ${vehicle.owner}
                                </span>

                            </div>


                            <div class="car-info-row">

                                <span class="car-info-label">
                                    연비
                                </span>

                                <span class="car-info-value">
                                    ${vehicle.fuel_efficiency} km/L
                                </span>

                            </div>

                        </div>
                    `;


                    vehicleList.appendChild(
                        card
                    );
                }
            );
        }


        // =====================================
        // 차량 등록
        // =====================================

        form.addEventListener(
            'submit',
            async function (event) {

                // HTML form의 기본 submit을 막음.
                // 페이지 전체가 새로고침되는 것을 방지함.
                event.preventDefault();


                // 입력값 읽기
                const formData =
                    new FormData(form);


                const vehicleData = {

                    owner:
                        formData.get(
                            'owner'
                        ),

                    vehicle_name:
                        formData.get(
                            'vehicle_name'
                        ),

                    fuel_efficiency:
                        Number(
                            formData.get(
                                'fuel_efficiency'
                            )
                        ),

                    fuel_type:
                        formData.get(
                            'fuel_type'
                        )
                };


                try {

                    // Flask 차량 등록 API 호출
                    const response =
                        await fetch(
                            '/api/vehicles',
                            {
                                method: 'POST',

                                headers: {
                                    'Content-Type':
                                        'application/json'
                                },

                                body:
                                    JSON.stringify(
                                        vehicleData
                                    )
                            }
                        );


                    const data =
                        await response.json();


                    if (!response.ok) {

                        throw new Error(
                            data.error ||
                            '차량 등록에 실패했습니다.'
                        );
                    }


                    // 등록 성공 메시지
                    alert(
                        '차량이 등록되었습니다.'
                    );


                    // 등록 모달 닫기
                    closeModal();


                    // DB 차량 목록을 다시 조회하여
                    // 새로 등록한 차량을 즉시 화면에 표시함.
                    await loadVehicles();


                } catch (error) {

                    console.error(
                        '차량 등록 오류:',
                        error
                    );

                    alert(
                        error.message
                    );
                }
            }
        );


        // =====================================
        // 페이지 진입 시 차량 목록 조회
        // =====================================

        loadVehicles();
    }
);