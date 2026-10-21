document.addEventListener('DOMContentLoaded', () => {
    const dataNode = document.getElementById('globe-flight-data');
    const section = document.querySelector('.route-globe-section');
    const orb = section?.querySelector('.globe-orb');
    const canvas = section?.querySelector('.globe-canvas');
    if (!dataNode || !section || !orb || !canvas) return;

    let flights;
    try { flights = JSON.parse(dataNode.textContent); } catch { return; }
    const context = canvas.getContext('2d');
    if (!context) return;
    const buttons = [...section.querySelectorAll('.globe-flight')];
    const fields = {
        number: section.querySelector('[data-globe-number]'),
        instance: section.querySelector('[data-globe-instance]'),
        status: section.querySelector('[data-globe-status]'),
        airport: section.querySelector('[data-globe-origin]'),
        aircraft: section.querySelector('[data-globe-aircraft]'),
        departure: section.querySelector('[data-globe-departure]'),
        arrival: section.querySelector('[data-globe-arrival]'),
        terminal: section.querySelector('[data-globe-terminal]'),
        gate: section.querySelector('[data-globe-gate]')
    };
    const plain = value => value == null || value === '' ? '—' : String(value);
    const statusClass = value => `flight-state-${String(value || 'unknown').toLowerCase().replace(/\s+/g, '-')}`;
    const land = [
        [[72,-165],[65,-150],[60,-135],[54,-128],[49,-124],[43,-123],[38,-119],[32,-116],[24,-108],[18,-104],[14,-92],[8,-84],[10,-78],[20,-77],[25,-80],[31,-81],[34,-75],[40,-73],[45,-66],[51,-56],[56,-60],[58,-70],[68,-80],[72,-100],[70,-125]],
        [[12,-81],[8,-77],[2,-79],[-5,-76],[-10,-72],[-18,-70],[-23,-66],[-30,-70],[-40,-73],[-52,-70],[-55,-65],[-45,-58],[-35,-53],[-25,-47],[-10,-38],[0,-50],[7,-59],[10,-69]],
        [[36,-10],[43,-9],[48,-6],[51,2],[56,5],[60,12],[68,20],[71,30],[65,42],[58,38],[55,30],[50,28],[47,22],[43,17],[40,18],[37,10]],
        [[36,-10],[33,-6],[30,0],[23,5],[15,0],[10,-5],[5,-3],[0,8],[-8,13],[-18,12],[-25,17],[-34,19],[-35,27],[-29,33],[-18,40],[-5,42],[5,35],[12,44],[20,38],[30,32],[32,22],[36,10]],
        [[70,42],[67,60],[60,75],[55,90],[52,105],[48,118],[42,130],[35,137],[30,130],[22,114],[10,108],[2,104],[5,96],[18,90],[21,80],[8,77],[7,70],[19,67],[25,58],[30,48],[38,45],[45,38],[52,42],[59,48]],
        [[-11,113],[-18,115],[-24,114],[-33,119],[-36,132],[-35,141],[-29,153],[-18,147],[-12,132]]
    ];

    const hubs = [
        [40.7,-74], [34,-118], [51.5,-.1], [25.2,55.3], [1.3,103.8], [35.7,139.7]
    ];
    const destinations = [
        [51.5,-.1], [35.7,139.7], [40.7,-74], [1.3,103.8], [-33.9,151.2], [34,-118]
    ];
    const routes = flights.map((_, i) => ({ from: hubs[i % hubs.length], to: destinations[i % destinations.length] }));
    let width = 0;
    let height = 0;
    let yaw = -0.55;
    let pitch = -0.14;
    let velocityX = 0;
    let velocityY = 0;
    let drag = null;
    let selectedIndex = 0;
    let animationFrame = 0;
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function initHomeMotion() {
        const home = document.querySelector('.main-container');
        if (!home) return;
        const sections = home.querySelectorAll('.overview-section, .board-section, .detail-grid, .infrastructure-section');
        const itemSelectors = {
            '.overview-section': '.section-heading, .stat-card',
            '.board-section': '.section-heading, .flight-mix-panel, .flight-card',
            '.detail-grid': '.detail-panel, .quick-panel',
            '.infrastructure-section': '.section-heading, .infrastructure-metrics, .ops-table-wrap'
        };
        sections.forEach(block => {
            block.classList.add('home-motion');
            const selector = Object.entries(itemSelectors).find(([key]) => block.matches(key))?.[1];
            block.querySelectorAll(selector || '').forEach((item,index) => {
                item.classList.add('home-motion-item');
                item.style.setProperty('--home-motion-delay', `${Math.min(index, 6) * 65}ms`);
            });
        });

        if (prefersReducedMotion || !('IntersectionObserver' in window)) {
            sections.forEach(block => block.classList.add('is-visible'));
            return;
        }
        const sectionObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (!entry.isIntersecting) return;
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            });
        }, { threshold:.08, rootMargin:'0px 0px -28px 0px' });
        sections.forEach(block => sectionObserver.observe(block));

        const counters = home.querySelectorAll('[data-count-up]');
        const countObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (!entry.isIntersecting) return;
                const node = entry.target;
                const target = Number(node.dataset.countUp);
                if (!Number.isFinite(target)) { observer.unobserve(node); return; }
                const start = performance.now();
                const duration = 900;
                const tick = now => {
                    const progress = Math.min((now - start) / duration, 1);
                    const eased = 1 - Math.pow(1 - progress, 3);
                    node.textContent = Math.round(target * eased).toLocaleString();
                    if (progress < 1) requestAnimationFrame(tick);
                };
                requestAnimationFrame(tick);
                observer.unobserve(node);
            });
        }, { threshold:.55 });
        counters.forEach(node => countObserver.observe(node));
    }
    initHomeMotion();

    function resize() {
        const rect = orb.getBoundingClientRect();
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        width = rect.width;
        height = rect.height;
        canvas.width = Math.round(width * dpr);
        canvas.height = Math.round(height * dpr);
        context.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    const resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(orb);
    resize();

    function project(lat, lon, centerX, centerY, radius) {
        const phi = lat * Math.PI / 180;
        const lambda = lon * Math.PI / 180 + yaw;
        const x0 = Math.cos(phi) * Math.sin(lambda);
        const y0 = Math.sin(phi);
        const z0 = Math.cos(phi) * Math.cos(lambda);
        const y = y0 * Math.cos(pitch) - z0 * Math.sin(pitch);
        const z = y0 * Math.sin(pitch) + z0 * Math.cos(pitch);
        return { x: centerX + radius * x0, y: centerY - radius * y, z };
    }

    function drawGlobe(now) {
        if (!width || !height) return;
        context.clearRect(0, 0, width, height);
        const cx = width / 2;
        const cy = height / 2;
        const radius = Math.min(width, height) * 0.425;
        const time = prefersReducedMotion ? 0 : now / 1000;

        // Soft star field and atmospheric rim give the globe some depth in the dark stage.
        for (let i = 0; i < 34; i++) {
            const x = (i * 137.5 + 29) % width;
            const y = (i * 79.3 + 17) % height;
            context.globalAlpha = .18 + ((i % 4) * .055);
            context.fillStyle = '#d9edf2';
            context.beginPath(); context.arc(x, y, i % 7 === 0 ? 1.25 : .7, 0, Math.PI * 2); context.fill();
        }
        context.globalAlpha = 1;
        context.save();
        context.shadowColor = 'rgba(66,181,221,.36)';
        context.shadowBlur = 25;
        const ocean = context.createRadialGradient(cx - radius * .36, cy - radius * .42, radius * .08, cx, cy, radius * 1.12);
        ocean.addColorStop(0, '#267397'); ocean.addColorStop(.48, '#14506f'); ocean.addColorStop(1, '#071d36');
        context.fillStyle = ocean;
        context.beginPath(); context.arc(cx, cy, radius, 0, Math.PI * 2); context.fill();
        context.restore();

        context.save();
        context.beginPath(); context.arc(cx, cy, radius, 0, Math.PI * 2); context.clip();
        // Surface latitude and longitude lines are projected onto the sphere, so they move with it.
        context.lineWidth = .7;
        context.strokeStyle = 'rgba(147,213,226,.19)';
        for (let lat = -75; lat <= 75; lat += 15) {
            context.beginPath(); let drawing = false;
            for (let lon = -180; lon <= 180; lon += 3) {
                const p = project(lat, lon, cx, cy, radius);
                if (p.z > 0) { if (!drawing) { context.moveTo(p.x,p.y); drawing = true; } else context.lineTo(p.x,p.y); }
                else drawing = false;
            }
            context.stroke();
        }
        for (let lon = -180; lon < 180; lon += 20) {
            context.beginPath(); let drawing = false;
            for (let lat = -90; lat <= 90; lat += 3) {
                const p = project(lat, lon, cx, cy, radius);
                if (p.z > 0) { if (!drawing) { context.moveTo(p.x,p.y); drawing = true; } else context.lineTo(p.x,p.y); }
                else drawing = false;
            }
            context.stroke();
        }

        // Simplified coastlines, projected as geographic coordinates rather than a flat map.
        land.forEach(polygon => {
            const points = polygon.map(([lat,lon]) => project(lat,lon,cx,cy,radius));
            const visible = points.filter(point => point.z > .02);
            if (visible.length < 3) return;
            context.beginPath();
            visible.forEach((point,index) => index ? context.lineTo(point.x,point.y) : context.moveTo(point.x,point.y));
            if (visible.length === points.length) context.closePath();
            if (visible.length === points.length) {
                const landFill = context.createLinearGradient(cx,cy-radius,cx,cy+radius);
                landFill.addColorStop(0,'rgba(114,174,148,.9)'); landFill.addColorStop(1,'rgba(43,119,110,.94)');
                context.fillStyle = landFill; context.fill();
            }
            context.strokeStyle = 'rgba(184,226,190,.42)'; context.lineWidth = 1.15; context.stroke();
        });

        // Flight paths bend above the surface and the plane markers progress along each route.
        routes.forEach((route,index) => {
            const progress = (time / 13 + index / Math.max(routes.length,1)) % 1;
            context.beginPath(); let drawing = false;
            for (let step = 0; step <= 50; step++) {
                const t = step / 50;
                const lat = route.from[0] + (route.to[0] - route.from[0]) * t + Math.sin(Math.PI * t) * 13;
                const lon = route.from[1] + (route.to[1] - route.from[1]) * t;
                const p = project(lat,lon,cx,cy,radius * (1 + .025 * Math.sin(Math.PI*t)));
                if (p.z > 0) { if (!drawing) { context.moveTo(p.x,p.y); drawing = true; } else context.lineTo(p.x,p.y); }
                else drawing = false;
            }
            context.setLineDash([3,6]); context.lineDashOffset = -time * 7;
            context.strokeStyle = index === selectedIndex ? 'rgba(255,207,137,.9)' : 'rgba(154,220,236,.54)';
            context.lineWidth = index === selectedIndex ? 1.8 : 1.1; context.stroke(); context.setLineDash([]);
            const lat = route.from[0] + (route.to[0] - route.from[0]) * progress + Math.sin(Math.PI * progress) * 13;
            const lon = route.from[1] + (route.to[1] - route.from[1]) * progress;
            const p = project(lat,lon,cx,cy,radius * (1 + .025 * Math.sin(Math.PI*progress)));
            const button = buttons[index];
            if (button) {
                button.style.left = `${p.x}px`; button.style.top = `${p.y}px`;
                button.classList.toggle('is-behind-globe', p.z <= .04);
            }
        });
        context.restore();

        // A directional light and lower limb shadow make this read as a sphere at a glance.
        const shade = context.createRadialGradient(cx-radius*.37,cy-radius*.45,radius*.25,cx+radius*.25,cy+radius*.3,radius*1.15);
        shade.addColorStop(0,'rgba(255,255,255,0)'); shade.addColorStop(.62,'rgba(1,12,28,.02)'); shade.addColorStop(1,'rgba(0,8,21,.58)');
        context.fillStyle = shade; context.beginPath(); context.arc(cx,cy,radius,0,Math.PI*2); context.fill();
        context.strokeStyle = 'rgba(151,221,242,.42)'; context.lineWidth = 1; context.beginPath(); context.arc(cx,cy,radius,0,Math.PI*2); context.stroke();

        if (!drag && !prefersReducedMotion) {
            yaw += velocityX; pitch = Math.max(-1.15, Math.min(1.15, pitch + velocityY));
            velocityX *= .94; velocityY *= .94;
            if (Math.abs(velocityX) < .00008) velocityX = 0;
            if (Math.abs(velocityY) < .00008) velocityY = 0;
        } else if (prefersReducedMotion) {
            velocityX = velocityY = 0;
        }
        animationFrame = requestAnimationFrame(drawGlobe);
    }
    animationFrame = requestAnimationFrame(drawGlobe);

    function selectFlight(index) {
        const flight = flights[index];
        if (!flight) return;
        selectedIndex = index;
        fields.number.textContent = plain(flight.Flight_Number);
        if (fields.instance) fields.instance.textContent = `INSTANCE #${plain(flight.Instance_ID)}`;
        fields.status.textContent = plain(flight.Instance_Status);
        fields.status.className = `flight-state ${statusClass(flight.Instance_Status)}`;
        fields.airport.textContent = plain(flight.Airport);
        fields.aircraft.textContent = plain(flight.Aircraft_Model);
        fields.departure.textContent = plain(flight.Scheduled_Departure);
        fields.arrival.textContent = plain(flight.Scheduled_Arrival);
        fields.terminal.textContent = `Terminal ${plain(flight.Terminal_Number)}`;
        fields.gate.textContent = plain(flight.Gate_Number);
        buttons.forEach((button, buttonIndex) => {
            const selected = buttonIndex === index;
            button.classList.toggle('is-selected', selected);
            button.setAttribute('aria-pressed', String(selected));
        });
    }

    const selectButtonFlight = event => {
        const target = event.target instanceof Element ? event.target.closest('.globe-flight') : null;
        if (!target || !section.contains(target)) return;
        if (event.type === 'click') event.preventDefault();
        selectFlight(Number(target.dataset.flight));
    };
    // Capture selection at the section so moving markers cannot swallow the activation event.
    section.addEventListener('pointerdown', selectButtonFlight, true);
    section.addEventListener('click', selectButtonFlight, true);
    if (flights.length) selectFlight(0);

    // Drag only on the canvas so a plane click is always delivered to its button.
    canvas.addEventListener('pointerdown', event => {
        if (event.button !== 0) return;
        drag = { pointerId:event.pointerId, x:event.clientX, y:event.clientY, lastX:event.clientX, lastY:event.clientY, time:performance.now() };
        velocityX = velocityY = 0;
        orb.classList.add('is-dragging');
        canvas.setPointerCapture(event.pointerId);
    });
    canvas.addEventListener('pointermove', event => {
        if (!drag || drag.pointerId !== event.pointerId) return;
        const dx = event.clientX - drag.lastX;
        const dy = event.clientY - drag.lastY;
        const now = performance.now();
        yaw += dx * .008;
        pitch = Math.max(-1.15,Math.min(1.15,pitch + dy * .008));
        const elapsed = Math.max(1,now - drag.time);
        velocityX = dx / elapsed * .012;
        velocityY = dy / elapsed * .012;
        drag.lastX = event.clientX; drag.lastY = event.clientY; drag.time = now;
    });
    const stopDrag = event => {
        if (!drag || drag.pointerId !== event.pointerId) return;
        drag = null; orb.classList.remove('is-dragging');
    };
    canvas.addEventListener('pointerup',stopDrag);
    canvas.addEventListener('pointercancel',stopDrag);
    canvas.addEventListener('lostpointercapture',stopDrag);

    document.addEventListener('visibilitychange', () => {
        if (document.hidden) cancelAnimationFrame(animationFrame);
        else animationFrame = requestAnimationFrame(drawGlobe);
    });
});
