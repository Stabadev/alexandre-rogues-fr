const button = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#navigation');
const smallScreen = window.matchMedia('(max-width: 650px)');
function closeMenu() {
  button.setAttribute('aria-expanded', 'false');
  navigation.toggleAttribute('data-closed', smallScreen.matches);
}
document.documentElement.classList.add('js');
button.hidden = !smallScreen.matches;
closeMenu();
button.addEventListener('click', () => {
  const open = button.getAttribute('aria-expanded') !== 'true';
  button.setAttribute('aria-expanded', String(open));
  navigation.toggleAttribute('data-closed', !open);
});
navigation.addEventListener('click', event => {
  if (event.target.closest('a') && smallScreen.matches) closeMenu();
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && button.getAttribute('aria-expanded') === 'true') {
    closeMenu(); button.focus();
  }
});
smallScreen.addEventListener('change', () => {
  button.hidden = !smallScreen.matches; closeMenu();
});
