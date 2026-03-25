<script>
	import '@evidence-dev/tailwind/fonts.css';
	import '../app.css';
	import { EvidenceDefaultLayout } from '@evidence-dev/core-components';
	import lightLogo from './assets/dataciviclab-wordmark-light.svg';
	import darkLogo from './assets/dataciviclab-wordmark-dark.svg';

	export let data;
</script>

<EvidenceDefaultLayout {data} {lightLogo} {darkLogo} builtWithEvidence={false}>
	<slot slot="content" />
</EvidenceDefaultLayout>
