import { VerdictLogged } from "../generated/VerdictRegistry/VerdictRegistry"
import { Case, VerdictLog } from "../generated/schema"

export function handleVerdictLogged(event: VerdictLogged): void {
  // caseId is `indexed string`, so the EVM only gives us its keccak256 hash
  // (as Bytes) — not recoverable to the original string. Use the tx hash as
  // the Case entity id (unique per tx) and store the hash as a hex string.
  let entityId = event.transaction.hash.toHexString()
  let caseIdHash = event.params.caseId.toHexString()

  // Upsert Case entity
  let caseEntity = Case.load(entityId)
  if (caseEntity == null) {
    caseEntity = new Case(entityId)
  }
  caseEntity.caseId          = caseIdHash
  caseEntity.verdictHash     = event.params.verdictHash
  caseEntity.verdict         = event.params.verdict
  caseEntity.confidenceScore = event.params.confidenceScore
  caseEntity.jurisdiction    = event.params.jurisdiction
  caseEntity.timestamp       = event.params.timestamp
  caseEntity.submitter       = event.params.submitter
  caseEntity.txHash          = event.transaction.hash
  caseEntity.blockNumber     = event.block.number
  caseEntity.save()

  // Create VerdictLog entry (one per event)
  let logId = event.transaction.hash.toHexString() + "-" + event.logIndex.toString()
  let log = new VerdictLog(logId)
  log.caseRef         = entityId
  log.verdictHash     = event.params.verdictHash
  log.verdict         = event.params.verdict
  log.confidenceScore = event.params.confidenceScore
  log.jurisdiction    = event.params.jurisdiction
  log.timestamp       = event.params.timestamp
  log.submitter       = event.params.submitter
  log.txHash          = event.transaction.hash
  log.blockNumber     = event.block.number
  log.save()
}
