/* =========================================================
   BLACK ARMY FRONTEND
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    /* =====================================================
       MOBILE MENU
    ====================================================== */

    const mobileButton =
        document.getElementById("mobileMenuButton");

    const mainNav =
        document.getElementById("mainNav");

    if (mobileButton && mainNav) {

        mobileButton.addEventListener("click", () => {

            mainNav.classList.toggle("open");

        });


        mainNav.querySelectorAll("a").forEach((link) => {

            link.addEventListener("click", () => {

                mainNav.classList.remove("open");

            });

        });

    }


    /* =====================================================
       REVEAL
    ====================================================== */

    const revealElements =
        document.querySelectorAll(".reveal");

    if ("IntersectionObserver" in window) {

        const observer =
            new IntersectionObserver(
                (entries) => {

                    entries.forEach((entry) => {

                        if (entry.isIntersecting) {

                            entry.target.classList.add("show");

                            observer.unobserve(
                                entry.target
                            );

                        }

                    });

                },
                {
                    threshold: 0.12
                }
            );


        revealElements.forEach((element) => {

            observer.observe(element);

        });

    } else {

        revealElements.forEach((element) => {

            element.classList.add("show");

        });

    }


    /* =====================================================
       COUNTERS
    ====================================================== */

    const counters =
        document.querySelectorAll(".counter");

    const animateCounter = (
        element,
        target
    ) => {

        const duration = 1300;

        const startTime =
            performance.now();


        const update = (currentTime) => {

            const elapsed =
                currentTime - startTime;

            const progress =
                Math.min(
                    elapsed / duration,
                    1
                );


            const eased =
                1 -
                Math.pow(
                    1 - progress,
                    3
                );


            const value =
                Math.floor(
                    target * eased
                );


            element.textContent =
                value.toLocaleString("fa-IR");


            if (progress < 1) {

                requestAnimationFrame(
                    update
                );

            } else {

                element.textContent =
                    target.toLocaleString("fa-IR");

            }

        };


        requestAnimationFrame(update);
    };


    if ("IntersectionObserver" in window) {

        const counterObserver =
            new IntersectionObserver(
                (entries) => {

                    entries.forEach((entry) => {

                        if (
                            entry.isIntersecting
                        ) {

                            const element =
                                entry.target;

                            const target =
                                Number(
                                    element.dataset.value || 0
                                );


                            animateCounter(
                                element,
                                target
                            );


                            counterObserver.unobserve(
                                element
                            );
                        }

                    });

                },
                {
                    threshold: 0.5
                }
            );


        counters.forEach((element) => {

            counterObserver.observe(element);

        });

    }


    /* =====================================================
       TOAST
    ====================================================== */

    window.showToast = function(message) {

        const container =
            document.getElementById(
                "toastContainer"
            );

        if (!container) {
            return;
        }


        const toast =
            document.createElement(
                "div"
            );

        toast.className = "toast";

        toast.textContent =
            message;


        container.appendChild(toast);


        setTimeout(() => {

            toast.classList.add(
                "hide"
            );


            setTimeout(() => {

                toast.remove();

            }, 300);

        }, 4000);

    };


    /* =====================================================
       PUBLIC NOTIFICATIONS
    ====================================================== */

    const publicBadge =
        document.getElementById(
            "notificationBadge"
        );

    const publicButton =
        document.getElementById(
            "notificationButton"
        );


    let lastPublicNewsId =
        Number(
            localStorage.getItem(
                "blackArmyLastNewsId"
            ) || 0
        );


    const updatePublicBadge = (
        count
    ) => {

        if (!publicBadge) {
            return;
        }

        publicBadge.textContent =
            String(count);

        publicBadge.style.display =
            count > 0
                ? "grid"
                : "none";
    };


    if (publicButton) {

        publicButton.addEventListener(
            "click",
            async () => {

                try {

                    const response =
                        await fetch(
                            "/api/public/news",
                            {
                                cache: "no-store"
                            }
                        );

                    const data =
                        await response.json();


                    if (data.length > 0) {

                        const latest =
                            Number(
                                data[0].id
                            );


                        const unread =
                            Math.max(
                                0,
                                latest -
                                lastPublicNewsId
                            );


                        updatePublicBadge(
                            unread
                        );


                        if (
                            "Notification" in window
                        ) {

                            if (
                                Notification.permission ===
                                "default"
                            ) {

                                await Notification.requestPermission();

                            }

                        }

                    }

                } catch (error) {

                    console.log(
                        "Public notification error:",
                        error
                    );

                }

            }
        );

    }


    const checkPublicNews =
        async () => {

            try {

                const response =
                    await fetch(
                        "/api/public/latest",
                        {
                            cache: "no-store"
                        }
                    );


                if (!response.ok) {
                    return;
                }


                const data =
                    await response.json();


                if (!data.news) {
                    return;
                }


                const newsId =
                    Number(
                        data.news.id
                    );


                if (
                    lastPublicNewsId === 0
                ) {

                    lastPublicNewsId =
                        newsId;

                    localStorage.setItem(
                        "blackArmyLastNewsId",
                        String(newsId)
                    );

                    updatePublicBadge(0);

                    return;

                }


                if (
                    newsId >
                    lastPublicNewsId
                ) {

                    const difference =
                        newsId -
                        lastPublicNewsId;


                    updatePublicBadge(
                        difference
                    );


                    showToast(
                        "📰 خبر جدید: " +
                        data.news.title
                    );


                    if (
                        "Notification" in window &&
                        Notification.permission ===
                        "granted"
                    ) {

                        new Notification(
                            "Black Army",
                            {
                                body:
                                    data.news.title,
                                icon:
                                    "/static/icon.png"
                            }
                        );

                    }


                    lastPublicNewsId =
                        newsId;

                    localStorage.setItem(
                        "blackArmyLastNewsId",
                        String(newsId)
                    );

                }

            } catch (error) {

                console.log(
                    "Latest news check failed:",
                    error
                );

            }

        };


    if (
        window.location.pathname === "/"
    ) {

        checkPublicNews();

        setInterval(
            checkPublicNews,
            10000
        );

    }


    /* =====================================================
       ADMIN NOTIFICATIONS
    ====================================================== */

    const adminBadge =
        document.getElementById(
            "adminBadge"
        );

    const joinCount =
        document.getElementById(
            "joinCount"
        );

    const messageCount =
        document.getElementById(
            "messageCount"
        );

    const adminButton =
        document.getElementById(
            "adminNotificationButton"
        );


    let lastAdminNotification =
        Number(
            localStorage.getItem(
                "blackArmyAdminNotice"
            ) || 0
        );


    const checkAdminNotifications =
        async () => {

            if (
                !window.location.pathname.startsWith(
                    "/admin/dashboard"
                )
            ) {
                return;
            }


            try {

                const response =
                    await fetch(
                        "/api/admin/notifications",
                        {
                            cache: "no-store"
                        }
                    );


                if (!response.ok) {
                    return;
                }


                const data =
                    await response.json();


                if (joinCount) {

                    joinCount.textContent =
                        data.pending_joins;

                }


                if (messageCount) {

                    messageCount.textContent =
                        data.unread_messages;

                }


                if (adminBadge) {

                    adminBadge.textContent =
                        data.pending_joins +
                        data.unread_messages;

                }


                const newestId =
                    Math.max(
                        data.latest_join
                            ? Number(
                                data.latest_join.id
                            )
                            : 0,

                        data.latest_message
                            ? Number(
                                data.latest_message.id
                            )
                            : 0
                    );


                if (
                    newestId >
                    lastAdminNotification
                ) {

                    if (
                        lastAdminNotification !== 0
                    ) {

                        showToast(
                            "🔔 مورد جدیدی برای بررسی داری."
                        );


                        if (
                            "Notification" in window &&
                            Notification.permission ===
                            "granted"
                        ) {

                            new Notification(
                                "Black Army Owner Panel",
                                {
                                    body:
                                        "درخواست یا پیام جدید ثبت شده است."
                                }
                            );

                        }

                    }


                    lastAdminNotification =
                        newestId;

                    localStorage.setItem(
                        "blackArmyAdminNotice",
                        String(
                            lastAdminNotification
                        )
                    );

                }

            } catch (error) {

                console.log(
                    "Admin notification error:",
                    error
                );

            }

        };


    if (adminButton) {

        adminButton.addEventListener(
            "click",
            async () => {

                if (
                    "Notification" in window &&
                    Notification.permission ===
                    "default"
                ) {

                    await Notification.requestPermission();

                }

                showToast(
                    "🔔 اعلان‌های پنل فعال شد."
                );

                checkAdminNotifications();

            }
        );

    }


    if (
        window.location.pathname.startsWith(
            "/admin/dashboard"
        )
    ) {

        checkAdminNotifications();

        setInterval(
            checkAdminNotifications,
            7000
        );

    }


    /* =====================================================
       SERVICE WORKER
    ====================================================== */

    if (
        "serviceWorker" in navigator
    ) {

        navigator.serviceWorker
            .register("/sw.js")
            .catch((error) => {

                console.log(
                    "Service Worker:",
                    error
                );

            });

    }

});
