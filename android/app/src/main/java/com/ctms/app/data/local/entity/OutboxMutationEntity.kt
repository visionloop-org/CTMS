package com.ctms.app.data.local.entity

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey
import java.util.UUID

/**
 * Prime Invariant #4: Offline-First Transactional Outbox Entity.
 * Scans, deliveries, and pickups commit immediately here before network dispatch.
 */
@Entity(
    tableName = "outbox_mutations",
    indices = [
        Index(value = ["status", "createdAt"]),
        Index(value = ["idempotencyKey"], unique = true)
    ]
)
data class OutboxMutationEntity(
    @PrimaryKey val mutationId: String = UUID.randomUUID().toString(),
    val eventType: String, // 'DELIVERY_COMPLETED', 'PICKUP_EMPTY', 'GATE_OUTWARD'
    val payloadJson: String, // Full JSON payload
    val idempotencyKey: String,
    val retryCount: Int = 0,
    val status: String = "QUEUED", // 'QUEUED', 'SYNCING', 'COMMITTED', 'FAILED'
    val lastError: String? = null,
    val createdAt: Long = System.currentTimeMillis()
)
