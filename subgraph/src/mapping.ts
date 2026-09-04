import { BigInt } from "@graphprotocol/graph-ts";
import { VerdictLogged } from "../generated/ModusOpsVerdict/ModusOpsVerdict";
import { Case, VerdictLog } from "../generated/schema";

const VERDICT_LABELS: string[] = ["PROCEED", "DISMISS", "ESCALATE", "REVIEW"];

export function handleVerdictLogged(event: VerdictLogged): void {
  const caseId = event.params.caseId;
  const findingHash = event.params.findingHash;
  const timestamp = event.params.timestamp;
  const verdictCode = event.params.verdict;

  let caseEntity = Case.load(caseId);
  if (caseEntity == null) {
    caseEntity = new Case(caseId);
    caseEntity.caseId = caseId;
    caseEntity.confidenceScore = 0;
    caseEntity.jurisdiction = "";
  }

  caseEntity.timestamp = timestamp;
  caseEntity.verdict = VERDICT_LABELS[verdictCode];
  caseEntity.txHash = event.transaction.hash;
  caseEntity.save();

  const verdictLogId =
    event.transaction.hash.toHex() + "-" + event.logIndex.toString();
  const verdictLog = new VerdictLog(verdictLogId);
  verdictLog.case = caseEntity.id;
  verdictLog.findingHash = findingHash;
  verdictLog.txHash = event.transaction.hash;
  verdictLog.blockNumber = event.block.number;
  // TODO: VerdictLogged does not currently emit an agent token id — the
  // contract event needs an added param before this can be populated.
  verdictLog.agentToken = BigInt.zero();
  verdictLog.timestamp = timestamp;
  verdictLog.save();
}
