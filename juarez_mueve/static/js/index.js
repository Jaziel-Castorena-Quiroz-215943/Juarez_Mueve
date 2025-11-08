document.addEventListener("DOMContentLoaded", function () {

    const hero = document.getElementById("hero");

    const imagenes = [
        hero.dataset.img1,
        hero.dataset.img2,
        hero.dataset.img3
    ];

    let index = 0;

    function cambiarImagen() {
        hero.classList.add("opacity-0");

        setTimeout(() => {
            index = (index + 1) % imagenes.length;
            hero.style.backgroundImage = `url('${imagenes[index]}')`;
            hero.classList.remove("opacity-0");
        }, 700);
    }

    setInterval(cambiarImagen, 5000);
});
