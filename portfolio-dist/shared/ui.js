document.documentElement.classList.add('js');

const menuButton = document.querySelector('[data-menu-toggle]');
const navigation = document.querySelector('#navigation');

if (menuButton && navigation) {
  const setMenu = (open) => {
    menuButton.setAttribute('aria-expanded', String(open));
    menuButton.textContent = open ? 'Закрыть' : 'Меню';
    navigation.classList.toggle('is-open', open);
  };
  menuButton.addEventListener('click', () => {
    setMenu(menuButton.getAttribute('aria-expanded') !== 'true');
  });
  navigation.addEventListener('click', (event) => {
    if (event.target.closest('a')) setMenu(false);
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && menuButton.getAttribute('aria-expanded') === 'true') {
      setMenu(false);
      menuButton.focus();
    }
  });
  matchMedia('(min-width: 761px)').addEventListener('change', () => setMenu(false));
}

const demoDialog = document.querySelector('#demo-dialog');
document.querySelectorAll('[data-demo]').forEach((button) => {
  button.addEventListener('click', () => demoDialog.showModal());
});

document.querySelectorAll('dialog').forEach((dialog) => {
  let opener;
  dialog.addEventListener('beforetoggle', (event) => {
    if (event.newState === 'open') opener = document.activeElement;
  });
  dialog.querySelector('[data-close]').addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => opener?.focus());
  dialog.addEventListener('keydown', (event) => {
    if (event.key !== 'Tab') return;
    const controls = [...dialog.querySelectorAll('button, a[href], select, [tabindex="0"]')]
      .filter((element) => !element.disabled && element.getClientRects().length > 0);
    const first = controls[0];
    const last = controls.at(-1);
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });
});

const filterButtons = document.querySelectorAll('[data-filter]');
const filterCards = document.querySelectorAll('[data-category]');
const filterStatus = document.querySelector('[data-filter-status]');
filterButtons.forEach((button) => {
  button.addEventListener('click', () => {
    filterButtons.forEach((item) => item.setAttribute('aria-pressed', String(item === button)));
    let visible = 0;
    filterCards.forEach((card) => {
      card.hidden = button.dataset.filter !== 'all' && card.dataset.category !== button.dataset.filter;
      if (!card.hidden) visible += 1;
    });
    filterStatus.textContent = `Показано услуг: ${visible}. Категория: ${button.textContent.trim()}.`;
  });
});

const gallery = document.querySelector('#gallery-dialog');
const galleryItems = [...document.querySelectorAll('[data-gallery]')];
if (gallery && galleryItems.length) {
  let index = 0;
  const showImage = (next) => {
    index = (next + galleryItems.length) % galleryItems.length;
    const item = galleryItems[index];
    const image = gallery.querySelector('img');
    image.src = item.dataset.image;
    image.alt = item.dataset.title;
    gallery.querySelector('[data-gallery-title]').textContent = item.dataset.title;
    gallery.querySelector('[data-gallery-position]').textContent = `${index + 1} из ${galleryItems.length}`;
  };
  galleryItems.forEach((button, position) => {
    button.addEventListener('click', () => {
      showImage(position);
      gallery.showModal();
    });
  });
  gallery.querySelector('[data-prev]').addEventListener('click', () => showImage(index - 1));
  gallery.querySelector('[data-next]').addEventListener('click', () => showImage(index + 1));
  gallery.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowRight') showImage(index + 1);
    if (event.key === 'ArrowLeft') showImage(index - 1);
  });
}
