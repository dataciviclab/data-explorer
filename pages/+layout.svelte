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
		const headerBrandLink = document.querySelector(
			'header div.flex.gap-x-4.items-center > a.text-sm.font-bold.text-base-content'
		);
		headerBrandLink?.setAttribute('data-dcl-brand-link', 'header');
		headerBrandLink
			?.querySelectorAll('img[alt="Home"]')
			.forEach((img) => img.setAttribute('data-dcl-wordmark', 'header'));

		const mobileDrawerBrandLink = document.querySelector(
			'div.bg-base-100.border-r.border-base-200.shadow-lg a.block.mt-1.text-sm.font-bold'
		);
		mobileDrawerBrandLink?.setAttribute('data-dcl-brand-link', 'drawer');
		mobileDrawerBrandLink
			?.querySelectorAll('img[alt="Home"]')
			.forEach((img) => img.setAttribute('data-dcl-wordmark', 'drawer'));
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
