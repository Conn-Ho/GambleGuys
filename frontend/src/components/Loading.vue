<template>
    <div class="loading-overlay">
      <div class="spinner"></div>
      <div class="loading-text">加载中，请稍候...</div>
    </div>
  </template>
  
  <style scoped>
  .loading-overlay {
    position: fixed;
    left: 0; top: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.5);
    z-index: 9999;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
  .spinner {
    width: 48px;
    height: 48px;
    border: 6px solid #eee;
    border-top: 6px solid #2563eb;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 16px;
  }
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  .loading-text {
    color: #fff;
    font-size: 18px;
    letter-spacing: 2px;
  }
  </style>