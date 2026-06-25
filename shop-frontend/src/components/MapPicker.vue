<script setup lang="ts">
import { ref, onMounted, watch, shallowRef, nextTick } from 'vue';
import { X, MapPin, Search, Navigation, Map } from 'lucide-vue-next';

const props = defineProps<{
  show: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'select', address: { province: string; city: string; district: string; detail: string; address: string }): void;
}>();

const searchKeyword = ref('');
const selectedAddress = ref('');
const manualAddress = ref('');
const showManualInput = ref(false);
const mapContainer = shallowRef<HTMLElement | null>(null);
const mapLoaded = ref(false);
const mapError = ref(false);

let map: any = null;
let marker: any = null;

const DEFAULT_CENTER = [116.397428, 39.90923];
const DEFAULT_ZOOM = 15;

function loadAMapScript(): Promise<void> {
  return new Promise((resolve, reject) => {
    // 高德 JS API 2.0 安全密钥配置：必须在加载地图 JS 之前设置
    // 否则逆地理编码等 Web 服务 API 会被服务端拦截
    // 注意：即使 AMap 已加载也要设置，因为可能在别的页面先加载了地图
    (window as any)._AMapSecurityConfig = {
      securityJsCode: '792def06c9ec4b7754ef8dd11a14b2dc',
    };

    if ((window as any).AMap) {
      // AMap 已存在，但需要重新注册插件以确保安全密钥生效
      resolve();
      return;
    }

    const script = document.createElement('script');
    script.src = 'https://webapi.amap.com/maps?v=2.0&key=1ddb21c774842530486ddb8f7f53cd11&securityJsCode=792def06c9ec4b7754ef8dd11a14b2dc&lang=zh_cn';
    script.type = 'text/javascript';
    script.charset = 'utf-8';

    const timeout = setTimeout(() => {
      mapError.value = true;
      reject(new Error('地图加载超时'));
    }, 15000);

    script.onload = () => {
      clearTimeout(timeout);
      resolve();
    };

    script.onerror = () => {
      clearTimeout(timeout);
      mapError.value = true;
      reject(new Error('地图加载失败'));
    };

    document.head.appendChild(script);
  });
}

async function initMap() {
  if (!mapContainer.value) return;

  try {
    await loadAMapScript();
    const AMap = (window as any).AMap;

    if (!AMap) {
      mapError.value = true;
      return;
    }

    map = new AMap.Map(mapContainer.value, {
      zoom: DEFAULT_ZOOM,
      center: DEFAULT_CENTER,
      resizeEnable: true,
    });

    map.on('click', (e: any) => {
      const { lng, lat } = e.lnglat;
      setMarker(lng, lat);
      reverseGeocode(lng, lat);
    });

    const toolbar = new (AMap.Toolbar || AMap.ToolBar)({
      position: 'LT',
    });
    map.addControl(toolbar);

    mapLoaded.value = true;
  } catch (error) {
    console.error('地图初始化失败:', error);
    mapError.value = true;
  }
}

function setMarker(lng: number, lat: number) {
  if (!map) return;

  if (marker) {
    map.remove(marker);
  }

  marker = new (window as any).AMap.Marker({
    position: [lng, lat],
    icon: new (window as any).AMap.Icon({
      size: new (window as any).AMap.Size(25, 34),
      image: '//webapi.amap.com/theme/v1.3/markers/n/mark_b.png',
      imageSize: new (window as any).AMap.Size(25, 34),
    }),
    offset: new (window as any).AMap.Pixel(-12.5, -34),
  });

  map.add(marker);
}

// 缓存逆地理编码解析出的结构化地址，点击"确定"时使用
const geocodeResult = ref<{ province: string; city: string; district: string; detail: string; address: string } | null>(null);

/**
 * 逆地理编码：将经纬度解析为省/市/区/详细地址
 * 使用高德 AMap.Geocoder 插件
 * 注意：只更新 selectedAddress 和 geocodeResult，不直接 emit
 * 用户必须点"确定"才提交结果
 */
function reverseGeocode(lng: number, lat: number) {
  const AMap = (window as any).AMap;
  if (!AMap) {
    selectedAddress.value = `(${lng.toFixed(4)}, ${lat.toFixed(4)})`;
    geocodeResult.value = null;
    return;
  }

  // 先显示坐标，等逆地理编码返回后更新为可读地址
  selectedAddress.value = '解析地址中...';

  AMap.plugin('AMap.Geocoder', () => {
    const geocoder = new AMap.Geocoder({
      radius: 1000,
      extensions: 'all',
    });

    geocoder.getAddress([lng, lat], (status: string, result: any) => {
      console.log('[MapPicker] 逆地理编码 status:', status, 'result:', result);
      if (status === 'complete' && result.regeocode) {
        const comp = result.regeocode.addressComponent;
        const formattedAddress = result.regeocode.formattedAddress || '';

        // 拼接详细地址：乡镇/街道 + 门牌号
        const detailParts = [
          comp.township || '',
          comp.street || '',
          comp.streetNumber || '',
        ].filter(Boolean).join('');
        const detail = detailParts || formattedAddress;

        // 缓存结构化数据，等用户点"确定"后再 emit
        geocodeResult.value = {
          province: comp.province || '',
          city: comp.city || comp.province || '',
          district: comp.district || '',
          detail: detail,
          address: formattedAddress,
        };

        // 显示完整地址
        selectedAddress.value = formattedAddress;
      } else {
        console.error('[MapPicker] 逆地理编码失败:', status, result);
        selectedAddress.value = `(${lng.toFixed(4)}, ${lat.toFixed(4)})`;
        geocodeResult.value = null;
      }
    });
  });
}

function handleSearch() {
  const keyword = searchKeyword.value.trim();
  if (!keyword) return;

  const AMap = (window as any).AMap;
  if (!AMap || !map) {
    selectedAddress.value = keyword;
    return;
  }

  AMap.plugin(['AMap.PlaceSearch'], () => {
    const placeSearch = new AMap.PlaceSearch({
      pageSize: 10,
      pageIndex: 1,
      city: '',
      map: map,
    });

    placeSearch.search(keyword, (status: string, result: any) => {
      if (status === 'complete' && result && result.poiList && result.poiList.pois && result.poiList.pois.length > 0) {
        const firstPoi = result.poiList.pois[0];
        if (firstPoi.location) {
          const { lng, lat } = firstPoi.location;
          map.setCenter([lng, lat]);
          map.setZoom(17);
          setMarker(lng, lat);
          // 搜索结果也通过逆地理编码获取结构化地址
          reverseGeocode(lng, lat);
        } else {
          selectedAddress.value = keyword;
        }
      } else {
        selectedAddress.value = keyword;
      }
    });
  });
}

function handleConfirm() {
  if (manualAddress.value.trim()) {
    // 手动输入：文本作为 detail，省市区留空让用户自行补充
    emit('select', {
      province: '',
      city: '',
      district: '',
      detail: manualAddress.value.trim(),
      address: manualAddress.value.trim(),
    });
  } else if (geocodeResult.value) {
    // 地图选点：使用逆地理编码缓存的结构化数据
    emit('select', geocodeResult.value);
  } else if (selectedAddress.value && !selectedAddress.value.startsWith('(') && selectedAddress.value !== '解析地址中...') {
    // 兜底：selectedAddress 有值但 geocodeResult 为空（如搜索结果未解析时点击确认）
    emit('select', {
      province: '',
      city: '',
      district: '',
      detail: selectedAddress.value,
      address: selectedAddress.value,
    });
  } else {
    alert('请在地图上点击选择位置，或手动输入地址');
  }
}

function handleLocate() {
  if (!navigator.geolocation) {
    alert('您的浏览器不支持地理位置服务');
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const lng = position.coords.longitude;
      const lat = position.coords.latitude;
      if (map) {
        map.setCenter([lng, lat]);
        map.setZoom(17);
        setMarker(lng, lat);
      }
      selectedAddress.value = `(${lng.toFixed(4)}, ${lat.toFixed(4)})`;
    },
    (error) => {
      alert('获取位置失败，请手动选择地址');
    },
    { enableHighAccuracy: true, timeout: 10000 }
  );
}

watch(() => props.show, (newVal) => {
  if (newVal && !map) {
    nextTick(() => {
      initMap();
    });
  }
});

onMounted(() => {
  if (props.show) {
    nextTick(() => {
      initMap();
    });
  }
});
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="fixed inset-0 z-50 flex items-end sm:items-center justify-center">
        <div class="absolute inset-0 bg-black/50" @click="emit('close')" />
        <div class="relative bg-white rounded-t-3xl sm:rounded-2xl shadow-2xl w-full sm:w-full max-w-3xl h-[92vh] sm:h-[90vh] max-h-[92vh] sm:max-h-[90vh] flex flex-col overflow-hidden">
          <div class="flex items-center justify-between px-6 py-4 border-b flex-shrink-0">
            <h3 class="font-display text-xl">选择收货地址</h3>
            <button class="p-2" @click="emit('close')">
              <X :size="20" />
            </button>
          </div>

          <div class="p-4 border-b bg-gold-50/30 flex-shrink-0">
            <div class="relative">
              <Search class="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5" />
              <input
                v-model="searchKeyword"
                type="text"
                placeholder="搜索地址"
                class="w-full pl-10 pr-12 py-3 border rounded-xl"
                @keyup.enter="handleSearch"
              />
              <button class="absolute right-2.5 top-1/2 -translate-y-1/2 p-2" @click="handleSearch">
                <Search :size="16" />
              </button>
            </div>
            <div class="mt-3">
              <button
                class="w-full py-2.5 px-4 border-1 border rounded-xl flex items-center justify-center gap-2 bg-white text-gold-800 hover:bg-indigo-600 hover:text-white transition-colors duration-200"
                @click="handleLocate"
              >
                <Navigation
                  :size="16"
                  class="text-gold-500 transition-colors duration-200"
                />
                <span class="font-medium">获取当前位置</span>
              </button>
            </div>
          </div>

          <div ref="mapContainer" class="h-64 sm:h-[340px] w-full relative bg-gray-100 flex-shrink-0">
            <div v-if="!mapLoaded && !mapError" class="absolute inset-0 flex items-center justify-center">
              <div class="flex flex-col items-center gap-3">
                <div class="w-12 h-12 border-4 border-gold-400 border-t-transparent rounded-full animate-spin" />
                <span>加载地图中...</span>
              </div>
            </div>
            <div v-if="mapError" class="absolute inset-0 flex items-center justify-center">
              <div class="flex flex-col items-center gap-4 p-8">
                <Map class="w-20 h-20" />
                <div class="text-center">
                  <p>地图加载失败</p>
                  <p>请检查网络连接或稍后重试</p>
                </div>
                <button class="px-6 py-2.5 bg-gold-400 text-white rounded-xl" @click="initMap">
                  重新加载地图
                </button>
              </div>
            </div>
          </div>

          <div class="flex-1 min-h-0 overflow-y-auto p-4">
            <!-- 地图选点结果 -->
            <div v-if="geocodeResult" class="mb-4 p-3 bg-indigo-50 rounded-xl border border-indigo-100">
              <div class="flex items-center gap-2 mb-2">
                <MapPin :size="16" class="text-indigo-500" />
                <span class="text-sm font-medium text-indigo-700">已识别地址</span>
              </div>
              <p class="text-sm text-gray-700 mb-2">{{ selectedAddress }}</p>
              <div class="grid grid-cols-3 gap-2 text-xs text-gray-500">
                <div><span class="text-gray-400">省</span> {{ geocodeResult.province || '-' }}</div>
                <div><span class="text-gray-400">市</span> {{ geocodeResult.city || '-' }}</div>
                <div><span class="text-gray-400">区</span> {{ geocodeResult.district || '-' }}</div>
              </div>
            </div>

            <!-- 未选点时的提示 -->
            <div v-else class="mb-4 p-4 border-2 border-dashed border-gray-200 rounded-xl text-center">
              <MapPin :size="24" class="mx-auto mb-2 text-gray-300" />
              <p class="text-sm text-gray-400">点击地图选择收货位置</p>
              <p class="text-xs text-gray-300 mt-1">或使用下方搜索 / 定位功能</p>
            </div>

            <!-- 手动输入：折叠为可展开的补充入口 -->
            <div class="mb-2">
              <button
                type="button"
                @click="showManualInput = !showManualInput"
                class="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg
                  :class="['w-3 h-3 transition-transform', showManualInput ? 'rotate-90' : '']"
                  fill="none" stroke="currentColor" viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
                手动输入地址（选填）
              </button>
              <input
                v-if="showManualInput"
                v-model="manualAddress"
                type="text"
                placeholder="门牌号、楼层等补充信息"
                class="w-full mt-2 px-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          <div class="p-4 border-t bg-white flex-shrink-0">
            <button
              class="w-full py-3.5 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              :disabled="!geocodeResult && !manualAddress.trim()"
              @click="handleConfirm"
            >
              确认选择地址
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active, .modal-leave-active {
  transition: all 0.3s ease;
}
.modal-enter-from, .modal-leave-to {
  opacity: 0;
}
.modal-enter-from > div:last-child, .modal-leave-to > div:last-child {
  transform: translateY(100%);
}
</style>
