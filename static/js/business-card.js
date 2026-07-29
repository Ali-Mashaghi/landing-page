(() => {
    const card = document.getElementById('businessCard');
    const flipButton = document.getElementById('businessCardFlip');
    const canvas = document.getElementById('businessCardBackground');

    if (!card || !flipButton || !canvas) {
        return;
    }

    const flipCard = () => {
        card.style.transform = '';
        card.classList.toggle('is-flipped');
    };

    card.addEventListener('click', flipCard);
    card.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            flipCard();
        }
    });
    flipButton.addEventListener('click', flipCard);

    card.addEventListener('mousemove', (event) => {
        if (card.classList.contains('is-flipped')) {
            return;
        }
        const bounds = card.getBoundingClientRect();
        const x = (event.clientX - bounds.left) / bounds.width - 0.5;
        const y = (event.clientY - bounds.top) / bounds.height - 0.5;
        card.style.transform = `rotateY(${x * 16}deg) rotateX(${-y * 11}deg) scale(1.02)`;
    });

    card.addEventListener('mouseleave', () => {
        if (!card.classList.contains('is-flipped')) {
            card.style.transform = '';
        }
    });

    const context = canvas.getContext('2d');
    let width;
    let height;
    let points = [];

    const createPoints = () => {
        points = [];
        const count = Math.min(Math.floor(width * height / 12000), 75);
        for (let index = 0; index < count; index += 1) {
            points.push({
                x: Math.random() * width,
                y: Math.random() * height,
                vx: (Math.random() - 0.5) * 0.24,
                vy: (Math.random() - 0.5) * 0.24,
                radius: Math.random() * 1.5 + 0.5,
                color: Math.random() > 0.5 ? '53,242,139' : '0,185,120',
                phase: Math.random() * Math.PI * 2,
            });
        }
    };

    const resize = () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
        createPoints();
    };

    const draw = () => {
        context.clearRect(0, 0, width, height);
        const glow = context.createRadialGradient(
            width * 0.5,
            height * 0.45,
            0,
            width * 0.5,
            height * 0.45,
            width * 0.65,
        );
        glow.addColorStop(0, 'rgba(53,242,139,.1)');
        glow.addColorStop(1, 'rgba(0,0,0,0)');
        context.fillStyle = glow;
        context.fillRect(0, 0, width, height);

        points.forEach((point) => {
            point.phase += 0.01;
            point.x += point.vx;
            point.y += point.vy;
            if (point.x < 0) point.x = width;
            if (point.x > width) point.x = 0;
            if (point.y < 0) point.y = height;
            if (point.y > height) point.y = 0;

            context.beginPath();
            context.arc(
                point.x,
                point.y,
                point.radius * (1 + 0.12 * Math.sin(point.phase)),
                0,
                Math.PI * 2,
            );
            context.fillStyle = `rgba(${point.color},${0.22 + 0.12 * Math.sin(point.phase)})`;
            context.fill();
        });

        window.requestAnimationFrame(draw);
    };

    window.addEventListener('resize', resize);
    resize();
    draw();
})();
