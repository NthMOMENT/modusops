import VerdictClient from './VerdictClient';

export function generateStaticParams() {
  return [{ id: 'placeholder' }];
}

export default function VerdictPage({ params }: { params: { id: string } }) {
  return <VerdictClient caseId={params.id} />;
}
