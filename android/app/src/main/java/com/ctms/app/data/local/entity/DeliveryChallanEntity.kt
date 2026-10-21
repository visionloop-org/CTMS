package com.ctms.app.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.UUID

@Entity(tableName = "local_delivery_challans")
data class DeliveryChallanEntity(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val challanNumber: String,
    val tripId: String?,
    val customerId: String,
    val challanType: String, // 'DELIVERY_FILLED', 'PICKUP_EMPTY'
    val signatureSvg: String?,
    val receiverName: String?,
    val receiverPhone: String?,
    val otpVerified: Boolean = false,
    val latitude: Double?,
    val longitude: Double?,
    val timestamp: Long = System.currentTimeMillis(),
    val syncStatus: String = "PENDING"
)
