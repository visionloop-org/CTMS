package com.ctms.app.data.local.dao

import androidx.room.*
import com.ctms.app.data.local.entity.CylinderCacheEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface CylinderDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertCylinders(cylinders: List<CylinderCacheEntity>)

    @Query("SELECT * FROM cylinders_cache WHERE serialNumber = :serial LIMIT 1")
    suspend fun findBySerialNumber(serial: String): CylinderCacheEntity?

    @Query("SELECT * FROM cylinders_cache WHERE qrCodeUid = :qrUid LIMIT 1")
    suspend fun findByQrCode(qrUid: String): CylinderCacheEntity?

    @Query("SELECT * FROM cylinders_cache WHERE rfidEpcUid = :rfid LIMIT 1")
    suspend fun findByRfid(rfid: String): CylinderCacheEntity?

    @Query("SELECT * FROM cylinders_cache WHERE isOverdue = 1")
    fun getOverdueCylinders(): Flow<List<CylinderCacheEntity>>

    @Query("SELECT COUNT(*) FROM cylinders_cache")
    suspend fun getCount(): Int
}
