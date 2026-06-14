
// BINNA shared interactions
(function(){
  function ready(fn){ if(document.readyState !== 'loading') fn(); else document.addEventListener('DOMContentLoaded', fn); }
  ready(function(){
    const menuBtn = document.getElementById('menu-btn') || document.getElementById('hamburger');
    const mobileNav = document.getElementById('mobile-nav') || document.getElementById('mobile-menu') || document.getElementById('sidebar');
    if(menuBtn && mobileNav){ menuBtn.addEventListener('click',()=> mobileNav.classList.toggle('hidden')); }
    document.querySelectorAll('[data-go]').forEach(el=> el.addEventListener('click',()=>{ location.href=el.getAttribute('data-go'); }));
    document.querySelectorAll('.approve-btn,.supplier-approve-btn').forEach(btn=>btn.addEventListener('click',()=>{ btn.textContent='تم القبول'; btn.classList.add('opacity-70'); }));
    document.querySelectorAll('.reject-btn,.supplier-reject-btn').forEach(btn=>btn.addEventListener('click',()=>{ btn.textContent='تم الرفض'; btn.classList.add('opacity-70'); }));
    document.querySelectorAll('.delete-user-btn').forEach(btn=>btn.addEventListener('click',()=>{ const row=btn.closest('tr'); if(row && confirm('هل تريد حذف هذا المستخدم؟')) row.remove(); }));
    document.querySelectorAll('.suspend-user-btn').forEach(btn=>btn.addEventListener('click',()=>{ btn.textContent = btn.textContent.includes('تفعيل') ? 'إيقاف' : 'تفعيل'; }));
  });
})();

document.addEventListener('DOMContentLoaded',()=>{const menu=document.getElementById('menu-btn');const mob=document.getElementById('mobile-nav');if(menu&&mob){menu.addEventListener('click',()=>mob.classList.toggle('open'))}document.querySelectorAll('[data-search]').forEach(input=>{const target=document.querySelector(input.dataset.search);if(!target)return;input.addEventListener('input',()=>{const q=input.value.trim().toLowerCase();target.querySelectorAll('[data-row]').forEach(row=>{row.style.display=row.innerText.toLowerCase().includes(q)?'':'none'})})});document.querySelectorAll('[data-filter]').forEach(select=>{select.addEventListener('change',()=>{const group=select.closest('.filter-group')||document;const target=document.querySelector(select.dataset.filterTarget||'#filter-area');if(!target)return;const filters=[...document.querySelectorAll('[data-filter]')];target.querySelectorAll('[data-row]').forEach(row=>{let show=true;filters.forEach(f=>{if(!f.value||f.value==='all')return;const key=f.dataset.filter;show=show&&row.dataset[key]===f.value});row.style.display=show?'':'none'})})});document.querySelectorAll('[data-confirm]').forEach(btn=>btn.addEventListener('click',()=>{btn.textContent=btn.dataset.confirm;btn.classList.remove('btn-dark');btn.classList.add('btn-green')}));document.querySelectorAll('[data-delete]').forEach(btn=>btn.addEventListener('click',()=>{const row=btn.closest('[data-row]');if(row&&confirm('هل أنت متأكد من الحذف؟'))row.remove()}));});
