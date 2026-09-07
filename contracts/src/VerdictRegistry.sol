// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.24;

/**
 * @title VerdictRegistry
 * @notice Immutable chain-of-custody record for Modus Ops adversarial AI verdicts.
 * @dev Each verdict is hashed off-chain (SHA-256) and committed here.
 *      The full verdict JSON is stored off-chain; only the hash is on-chain.
 *      Indexed by The Graph via VerdictLogged events.
 */
contract VerdictRegistry {

    // -----------------------------------------------------------------------
    // Types
    // -----------------------------------------------------------------------

    enum VerdictType { PROCEED, DISMISS, ESCALATE, REVIEW }
    enum Jurisdiction { LOCAL, STATE, FEDERAL }

    struct VerdictRecord {
        string  caseId;
        bytes32 verdictHash;       // SHA-256 of the full VerdictObject JSON
        VerdictType verdict;
        uint8   confidenceScore;   // 0–100
        Jurisdiction jurisdiction;
        uint256 timestamp;
        address submitter;
        uint256[4] agentTokens;    // [1416, 1417, 1418, 1419]
    }

    // -----------------------------------------------------------------------
    // State
    // -----------------------------------------------------------------------

    address public immutable owner;
    uint256 public verdictCount;

    // caseId string → on-chain index (1-based; 0 means not found)
    mapping(string => uint256) private _caseIndex;

    // 1-based index → record
    mapping(uint256 => VerdictRecord) private _records;

    // -----------------------------------------------------------------------
    // Events
    // -----------------------------------------------------------------------

    /**
     * @notice Emitted on every committed verdict. Indexed by The Graph.
     * @param caseId        Human-readable case identifier (e.g. "OBE-2026-001")
     * @param verdictHash   SHA-256 of the full VerdictObject JSON (bytes32)
     * @param verdict       PROCEED | DISMISS | ESCALATE | REVIEW
     * @param confidenceScore 0–100
     * @param jurisdiction  LOCAL | STATE | FEDERAL
     * @param timestamp     Unix timestamp (seconds)
     * @param submitter     Address that committed the verdict
     */
    event VerdictLogged(
        string  indexed caseId,
        bytes32 indexed verdictHash,
        VerdictType     verdict,
        uint8           confidenceScore,
        Jurisdiction    jurisdiction,
        uint256         timestamp,
        address indexed submitter
    );

    // -----------------------------------------------------------------------
    // Errors
    // -----------------------------------------------------------------------

    error Unauthorized();
    error CaseAlreadyExists(string caseId);
    error InvalidConfidenceScore(uint8 score);
    error EmptyCaseId();

    // -----------------------------------------------------------------------
    // Constructor
    // -----------------------------------------------------------------------

    constructor() {
        owner = msg.sender;
    }

    // -----------------------------------------------------------------------
    // Write
    // -----------------------------------------------------------------------

    /**
     * @notice Commit a verdict on-chain. Callable by owner only.
     * @param caseId          Unique case identifier string.
     * @param verdictHash     SHA-256 of the full VerdictObject JSON as bytes32.
     * @param verdict         Enum: 0=PROCEED, 1=DISMISS, 2=ESCALATE, 3=REVIEW.
     * @param confidenceScore 0–100 integer.
     * @param jurisdiction    Enum: 0=LOCAL, 1=STATE, 2=FEDERAL.
     */
    function commitVerdict(
        string calldata caseId,
        bytes32 verdictHash,
        VerdictType verdict,
        uint8 confidenceScore,
        Jurisdiction jurisdiction
    ) external returns (uint256 index) {
        if (msg.sender != owner) revert Unauthorized();
        if (bytes(caseId).length == 0) revert EmptyCaseId();
        if (_caseIndex[caseId] != 0) revert CaseAlreadyExists(caseId);
        if (confidenceScore > 100) revert InvalidConfidenceScore(confidenceScore);

        unchecked { ++verdictCount; }
        index = verdictCount;

        uint256[4] memory tokens = [uint256(1416), uint256(1417), uint256(1418), uint256(1419)];

        _records[index] = VerdictRecord({
            caseId:          caseId,
            verdictHash:     verdictHash,
            verdict:         verdict,
            confidenceScore: confidenceScore,
            jurisdiction:    jurisdiction,
            timestamp:       block.timestamp,
            submitter:       msg.sender,
            agentTokens:     tokens
        });

        _caseIndex[caseId] = index;

        emit VerdictLogged(
            caseId,
            verdictHash,
            verdict,
            confidenceScore,
            jurisdiction,
            block.timestamp,
            msg.sender
        );
    }

    // -----------------------------------------------------------------------
    // Read
    // -----------------------------------------------------------------------

    /**
     * @notice Retrieve a verdict record by its 1-based index.
     */
    function getVerdictByIndex(uint256 index) external view returns (VerdictRecord memory) {
        return _records[index];
    }

    /**
     * @notice Retrieve a verdict record by case ID string.
     */
    function getVerdictByCaseId(string calldata caseId) external view returns (VerdictRecord memory) {
        uint256 index = _caseIndex[caseId];
        return _records[index];
    }

    /**
     * @notice Check whether a case ID has been committed.
     */
    function caseExists(string calldata caseId) external view returns (bool) {
        return _caseIndex[caseId] != 0;
    }
}
