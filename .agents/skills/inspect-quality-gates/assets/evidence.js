/* 検索中も該当帳票の祖先を保ち、現在位置とfocusを更新する。 */
const search = document.querySelector('#search');
search.addEventListener('input', () => {
  const query = search.value.toLocaleLowerCase();
  document.querySelectorAll('article').forEach(article => {
    article.hidden = !article.textContent.toLocaleLowerCase().includes(query);
  });
  document.querySelectorAll('[data-target]').forEach(leaf => {
    leaf.hidden = document.getElementById(leaf.dataset.target).hidden;
  });
  [...document.querySelectorAll('details.hierarchy')].reverse().forEach(branch => {
    branch.hidden = ![...branch.querySelectorAll('[data-target]')].some(leaf => !leaf.hidden);
    if (query && !branch.hidden) branch.open = true;
  });
});
function locationChanged() {
  const article = document.getElementById(location.hash.slice(1));
  if (!article?.dataset.breadcrumb) return;
  document.querySelector('#location').textContent = article.dataset.breadcrumb;
  document.querySelectorAll('aside a').forEach(link => {
    if (link.hash === location.hash) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
}
window.addEventListener('hashchange', locationChanged);
locationChanged();
const dialog = document.querySelector('#zoom');
let origin;
document.querySelectorAll('.image').forEach(button => button.addEventListener('click', () => {
  origin = button;
  dialog.querySelector('img').src = button.querySelector('img').src;
  dialog.showModal();
}));
dialog.querySelector('button').addEventListener('click', () => dialog.close());
dialog.addEventListener('close', () => origin?.focus());
