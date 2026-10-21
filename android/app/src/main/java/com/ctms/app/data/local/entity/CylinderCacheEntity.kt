package com.ctms.app.data.local.entity

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey
import java.util.UUID

/**
 * Local cache of cylinders for fast zero-latency offline QR/RFID scanning.
 */
@Entity(
    tableName = "cylinders_cache",
    indices = [
        Index(value = ["serialNumber"], unique = true),
        Index(value = ["qrCodeUid"], unique = true),
        Index(value = ["rfidEpcUid"], unique = true)
    ]
)
data class CylinderCacheEntity(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val serialNumber: String,
    val qrCodeUid: String? = null,
    val rfidEpcUid: String? = null,
    val gasType: String,
    val ownership: String, // 'COC', 'POC', 'VOC'
    val ownerCustomerId: String? = null,
    val stampedTareWeightKg: Double,
    val currentTareWeightKg: Double? = null,
    val hydroTestDueDate: Long, // Epoch millis
    val isOverdue: Boolean = false,
    val status: String = "PLANT_EMPTY",
    val lastSyncedAt: Long = System.currentTimeMillis()
)
