<script>
	import '@evidence-dev/tailwind/fonts.css';
	import '../app.css';
	import { EvidenceDefaultLayout } from '@evidence-dev/core-components';
	import { showQueries } from '@evidence-dev/component-utilities/stores';
	import { onMount } from 'svelte';
	import lightLogo from './assets/dataciviclab-wordmark-light.svg';
	import darkLogo from './assets/dataciviclab-wordmark-dark.svg';

	export let data;
	const queriesInitKey = 'dcl_showQueries_initialized';

	const syncBrandTargets = () => {
		document.querySelectorAll('header img[alt="Home"]').forEach((img) => {
			img.setAttribute('data-dcl-wordmark', 'header');
			img.closest('a')?.setAttribute('data-dcl-brand-link', 'header');
		});

		[...document.querySelectorAll('img[alt="Home"]')]
			.filter((img) => !img.closest('header'))
			.forEach((img) => {
				img.setAttribute('data-dcl-wordmark', 'drawer');
				img.closest('a')?.setAttribute('data-dcl-brand-link', 'drawer');
				img.src = img.className.includes('dark:block') ? darkLogo : lightLogo;
			});
	};

	onMount(() => {
		if (localStorage.getItem(queriesInitKey) === null) {
			showQueries.set(true);
			localStorage.setItem(queriesInitKey, 'true');
		}

		syncBrandTargets();

		const observer = new MutationObserver(() => {
			syncBrandTargets();
		});

		observer.observe(document.body, {
			childList: true,
			subtree: true
		});

		return () => observer.disconnect();
	});
</script>

<EvidenceDefaultLayout {data} {lightLogo} {darkLogo} builtWithEvidence={false}>
	<slot slot="content" />
</EvidenceDefaultLayout>
