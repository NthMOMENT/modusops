import CasePipelineClient from './CasePipelineClient';

export function generateStaticParams() {
  return [{ id: 'placeholder' }];
}

export default function CasePipeline({ params }: { params: { id: string } }) {
  return <CasePipelineClient caseId={params.id} />;
}
