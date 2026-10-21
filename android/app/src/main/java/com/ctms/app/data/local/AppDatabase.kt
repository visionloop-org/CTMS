package com.ctms.app.data.local

import androidx.room.Database
import androidx.room.RoomDatabase
import com.ctms.app.data.local.dao.CylinderDao
import com.ctms.app.data.local.dao.OutboxDao
import com.ctms.app.data.local.entity.CylinderCacheEntity
import com.ctms.app.data.local.entity.DeliveryChallanEntity
import com.ctms.app.data.local.entity.OutboxMutationEntity

@Database(
    entities = [
        CylinderCacheEntity::class,
        OutboxMutationEntity::class,
        DeliveryChallanEntity::class
    ],
    version = 1,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun cylinderDao(): CylinderDao
    abstract fun outboxDao(): OutboxDao
}
