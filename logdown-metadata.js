const type2status = {draft: 'icon-inbox', published: 'icon-globe', private_mode: 'icon-lock'};

const z = [...document.querySelectorAll('ul.logdown-posts-list li.post')]
	.map(l => {
		const cl = l.classList;
		cl.remove('group', 'post');
		const ret = {
			type: cl.item(0),
			id: l.id,
			title: l.querySelector('.post-title').textContent,
			status: l.querySelector('.post-status i').className,
			timestamp: l.querySelector('.post-timestamp').textContent,
		};
		cl.add('group', 'post');
		return ret;
	});

console.assert(z.every(l => type2status[l.type]===l.status));
