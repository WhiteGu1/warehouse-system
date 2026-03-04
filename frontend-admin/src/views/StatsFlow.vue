<template>
  <div>
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px">
      <el-button @click="$router.push('/stats')" :icon="ArrowLeft">返回</el-button>
      <h2 style="margin:0">流水统计</h2>
    </div>

    <el-card style="margin-bottom:20px">
      <div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap">
        <span style="font-weight:bold;font-size:15px">统计时间段</span>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          style="width:280px"
          @change="loadAll"
        />
        <el-button @click="setToday">今天</el-button>
        <el-button @click="setThisWeek">本周</el-button>
        <el-button @click="setThisMonth">本月</el-button>
      </div>
    </el-card>

    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>流水明细</span>
          <div style="display:flex;gap:16px">
            <span style="color:#67c23a;font-weight:bold">销售收入：¥{{ flowData.total_sales }}</span>
            <span style="color:#f56c6c;font-weight:bold">入库支出：¥{{ flowData.total_cost }}</span>
            <span :style="flowData.profit >= 0 ? 'color:#67c23a;font-weight:bold' : 'color:#f56c6c;font-weight:bold'">
              {{ flowData.profit >= 0 ? '盈利' : '亏损' }}：¥{{ Math.abs(flowData.profit) }}
            </span>
          </div>
        </div>
      </template>
      <el-table :data="flowData.records" stripe max-height="600">
        <el-table-column prop="time" label="时间" width="160" />
        <el-table-column label="类型" width="80">
          <template #default="{ row }">
            <el-tag :type="row.type === '销售' ? 'success' : 'warning'" size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="product_name" label="商品名称" />
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="unit_price" label="单价" width="90">
          <template #default="{ row }">¥{{ row.unit_price }}</template>
        </el-table-column>
        <el-table-column label="金额" width="110">
          <template #default="{ row }">
            <span :style="row.type === '销售' ? 'color:#67c23a;font-weight:bold' : 'color:#f56c6c'">
              {{ row.type === '销售' ? '+' : '-' }}¥{{ row.amount }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" show-overflow-tooltip />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ArrowLeft } from '@element-plus/icons-vue'
import request from '../utils/request'

const dateRange = ref(null)
const flowData = ref({ total_sales: 0, total_cost: 0, profit: 0, records: [] })

const getParams = () => {
  if (dateRange.value && dateRange.value[0]) {
    return { start: dateRange.value[0], end: dateRange.value[1] }
  }
  const today = new Date().toISOString().slice(0, 10)
  return { start: today, end: today }
}

const loadAll = async () => {
  const params = getParams()
  flowData.value = await request.get('/stats/flow', { params })
}

const setToday = () => {
  const today = new Date().toISOString().slice(0, 10)
  dateRange.value = [today, today]
  loadAll()
}

const setThisWeek = () => {
  const now = new Date()
  const day = now.getDay() || 7
  const mon = new Date(now)
  mon.setDate(now.getDate() - day + 1)
  dateRange.value = [mon.toISOString().slice(0, 10), now.toISOString().slice(0, 10)]
  loadAll()
}

const setThisMonth = () => {
  const now = new Date()
  const first = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().slice(0, 10)
  dateRange.value = [first, now.toISOString().slice(0, 10)]
  loadAll()
}

onMounted(() => {
  setToday()
})
</script>