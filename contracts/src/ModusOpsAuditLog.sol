// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract ModusOpsAuditLog {

    event FindingLogged(
        bytes32 indexed findingHash,
        string  indexed caseId,
        address indexed reporter,
        uint256 timestamp,
        uint8   confidenceScore,
        Verdict verdict
    );
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
    event ReporterAdded(address indexed reporter);
    event ReporterRemoved(address indexed reporter);

    enum Verdict { PROCEED, HOLD, DISMISS }

    struct Finding {
        bytes32 findingHash;
        string  caseId;
        address reporter;
        uint256 timestamp;
        uint8   confidenceScore;
        Verdict verdict;
        bool    exists;
    }

    address public owner;
    mapping(string => bytes32[]) public caseFindingHashes;
    mapping(bytes32 => Finding) public findings;
    mapping(address => bool) public authorizedReporters;
    uint256 public totalFindings;

    modifier onlyOwner() {
        require(msg.sender == owner, "ModusOps: not owner");
        _;
    }

    modifier onlyAuthorized() {
        require(
            authorizedReporters[msg.sender] || msg.sender == owner,
            "ModusOps: not authorized reporter"
        );
        _;
    }

    constructor() {
        owner = msg.sender;
        authorizedReporters[msg.sender] = true;
        emit OwnershipTransferred(address(0), msg.sender);
        emit ReporterAdded(msg.sender);
    }

    function logFinding(
        string  calldata caseId,
        bytes32          findingHash,
        uint8            confidenceScore,
        Verdict          verdict
    ) external onlyAuthorized returns (bytes32) {
        require(bytes(caseId).length > 0,      "ModusOps: empty caseId");
        require(bytes(caseId).length <= 128,   "ModusOps: caseId too long");
        require(confidenceScore <= 100,         "ModusOps: score out of range");
        require(!findings[findingHash].exists,  "ModusOps: finding already logged");

        findings[findingHash] = Finding({
            findingHash:     findingHash,
            caseId:          caseId,
            reporter:        msg.sender,
            timestamp:       block.timestamp,
            confidenceScore: confidenceScore,
            verdict:         verdict,
            exists:          true
        });

        caseFindingHashes[caseId].push(findingHash);
        totalFindings++;

        emit FindingLogged(findingHash, caseId, msg.sender, block.timestamp, confidenceScore, verdict);
        return findingHash;
    }

    function getCaseFindingHashes(string calldata caseId) external view returns (bytes32[] memory) {
        return caseFindingHashes[caseId];
    }

    function getFinding(bytes32 findingHash) external view returns (Finding memory) {
        require(findings[findingHash].exists, "ModusOps: finding not found");
        return findings[findingHash];
    }

    function verifyFinding(bytes32 findingHash) external view returns (bool) {
        return findings[findingHash].exists;
    }

    function addReporter(address reporter) external onlyOwner {
        authorizedReporters[reporter] = true;
        emit ReporterAdded(reporter);
    }

    function removeReporter(address reporter) external onlyOwner {
        require(reporter != owner, "ModusOps: cannot remove owner");
        authorizedReporters[reporter] = false;
        emit ReporterRemoved(reporter);
    }

    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "ModusOps: zero address");
        emit OwnershipTransferred(owner, newOwner);
        emit ReporterRemoved(owner);
        owner = newOwner;
        authorizedReporters[newOwner] = true;
        emit ReporterAdded(newOwner);
    }
}
