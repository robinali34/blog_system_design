---
layout: post
title: "Design a JNI (Java Native Interface) Bridge - OS Frameworks Interview"
date: 2025-11-03
categories: [System Design, Interview Example, OS Frameworks, Android, JNI]
excerpt: "A detailed walkthrough of designing a JNI bridge for efficient data transfer, memory management, error handling, performance optimization, and thread safety between Java and native code."
---

## Introduction

This post provides a comprehensive walkthrough of designing a JNI (Java Native Interface) Bridge, a common interview question for Meta's Software Engineer - OS Frameworks role. JNI bridges are critical components in Android frameworks that enable communication between Java and native (C/C++) code, requiring careful design for performance, memory safety, and reliability.

## Problem Statement

**Design a JNI (Java Native Interface) Bridge that addresses:**

1. **Efficient data transfer between Java and native code**: Minimize overhead when passing data across the JNI boundary
2. **Memory management across boundaries**: Properly manage memory in both Java and native code, prevent leaks
3. **Error handling and exception propagation**: Handle errors gracefully and propagate exceptions correctly
4. **Performance optimization**: Minimize JNI call overhead, optimize for frequent operations
5. **Thread safety considerations**: Ensure thread-safe operations across Java and native boundaries

**Describe the architecture, design patterns, and implementation considerations for building a robust JNI bridge.**

## Understanding JNI

### What is JNI?

JNI (Java Native Interface) is a programming framework that allows Java code running in a Java Virtual Machine (JVM) to call and be called by native applications (written in C/C++) and libraries. It's essential for:

- Accessing system-level APIs not available in Java
- Reusing existing C/C++ libraries
- Performance-critical operations
- Direct hardware access

### JNI Challenges

1. **Performance Overhead**: JNI calls have significant overhead compared to regular Java method calls
2. **Memory Management**: Different memory models between Java (garbage collected) and C/C++ (manual)
3. **Error Handling**: Exceptions in Java vs. error codes in C/C++
4. **Thread Safety**: JNI environment is thread-local, requires careful handling
5. **Type Mapping**: Converting between Java and native types
6. **Reference Management**: Managing local and global references

## Step 1: Requirements Gathering

### Functional Requirements

1. **Data Transfer**
   - Transfer primitive types (int, float, double, etc.)
   - Transfer objects (arrays, strings, custom objects)
   - Transfer large data efficiently (buffers, byte arrays)
   - Minimize copying overhead
   - Support bidirectional data flow

2. **Memory Management**
   - Prevent memory leaks in native code
   - Properly release Java references
   - Manage native memory allocation/deallocation
   - Handle out-of-memory scenarios
   - Track and debug memory leaks

3. **Error Handling**
   - Convert native error codes to Java exceptions
   - Propagate Java exceptions from native code
   - Handle exceptions without crashing
   - Provide meaningful error messages
   - Log errors for debugging

4. **Performance**
   - Minimize JNI call overhead
   - Cache JNI references and method IDs
   - Batch operations when possible
   - Use direct buffers for large data
   - Optimize hot paths

5. **Thread Safety**
   - Support multi-threaded access
   - Properly attach/detach threads
   - Synchronize access to shared resources
   - Handle concurrent modifications

### Non-Functional Requirements

**Performance:**
- JNI call overhead: < 100ns for simple operations
- Data transfer: < 1ms for 1MB data
- Memory overhead: < 10% of data size

**Reliability:**
- No memory leaks
- Graceful error handling
- No crashes from improper JNI usage

**Maintainability:**
- Clear API design
- Comprehensive error messages
- Easy to debug and profile

## Step 2: High-Level Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Java Layer (Android Framework)             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Java API    │  │  Bridge      │  │  Error       │      │
│  │  Interface   │  │  Manager     │  │  Handler     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ JNI Boundary
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    JNI Bridge Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Reference   │  │  Type        │  │  Memory      │      │
│  │  Manager     │  │  Converter   │  │  Manager     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Call        │  │  Thread      │  │  Performance │      │
│  │  Optimizer   │  │  Manager     │  │  Monitor     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Native Layer (C/C++)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Native      │  │  Memory      │  │  Error       │      │
│  │  Functions   │  │  Allocator   │  │  Codes       │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

1. **Java API Layer**: Public interface for Java code
2. **JNI Bridge Manager**: Coordinates JNI operations
3. **Reference Manager**: Manages Java object references
4. **Type Converter**: Converts between Java and native types
5. **Memory Manager**: Handles memory allocation/deallocation
6. **Error Handler**: Handles exceptions and error propagation
7. **Thread Manager**: Manages thread attachment/detachment
8. **Call Optimizer**: Optimizes JNI call performance

## Step 3: Detailed Design

### 1. Efficient Data Transfer

#### Primitive Type Transfer

**Direct Transfer (No Copying):**
```java
// Java side
public class JNIBridge {
    static {
        System.loadLibrary("native_lib");
    }
    
    // Direct primitive transfer
    public native int processInt(int value);
    public native float processFloat(float value);
    public native double processDouble(double value);
    public native boolean processBoolean(boolean value);
}
```

```cpp
// Native side
JNIEXPORT jint JNICALL
Java_JNIBridge_processInt(JNIEnv *env, jobject thiz, jint value) {
    // Direct access, no copying
    return value * 2;
}
```

#### Array Transfer

**Critical Performance Consideration:**
- Use `GetPrimitiveArrayCritical` for direct access (fastest)
- Use `GetArrayElements` for safer access
- Always release arrays to prevent memory leaks

```cpp
JNIEXPORT jintArray JNICALL
Java_JNIBridge_processIntArray(JNIEnv *env, jobject thiz, jintArray array) {
    // Get array elements
    jint *elements = env->GetIntArrayElements(array, NULL);
    if (elements == NULL) {
        return NULL; // OutOfMemoryError already thrown
    }
    
    jsize length = env->GetArrayLength(array);
    
    // Process array in native code (fast)
    for (jsize i = 0; i < length; i++) {
        elements[i] = elements[i] * 2;
    }
    
    // Release array (CRITICAL: prevents memory leak)
    env->ReleaseIntArrayElements(array, elements, 0);
    
    return array;
}
```

#### Direct ByteBuffer for Large Data

**For large data transfers (e.g., images, audio):**

```java
// Java side
public native void processLargeData(ByteBuffer buffer, int size);

// Usage
ByteBuffer buffer = ByteBuffer.allocateDirect(1024 * 1024); // 1MB
// Fill buffer...
bridge.processLargeData(buffer, buffer.capacity());
```

```cpp
JNIEXPORT void JNICALL
Java_JNIBridge_processLargeData(JNIEnv *env, jobject thiz, 
                                jobject buffer, jint size) {
    // Get direct buffer address (zero-copy)
    void *ptr = env->GetDirectBufferAddress(buffer);
    if (ptr == NULL) {
        // Not a direct buffer, handle error
        return;
    }
    
    // Process data directly (no copying)
    processNativeData(ptr, size);
}
```

#### Object Transfer

**For custom objects:**

```java
// Java side
public class DataObject {
    public int value;
    public String name;
    public float[] array;
}

public native void processObject(DataObject obj);
```

```cpp
// Native side
JNIEXPORT void JNICALL
Java_JNIBridge_processObject(JNIEnv *env, jobject thiz, jobject obj) {
    // Get object class
    jclass clazz = env->GetObjectClass(obj);
    
    // Get field IDs (should be cached, not fetched every call)
    jfieldID valueField = env->GetFieldID(clazz, "value", "I");
    jfieldID nameField = env->GetFieldID(clazz, "name", "Ljava/lang/String;");
    jfieldID arrayField = env->GetFieldID(clazz, "array", "[F");
    
    // Get field values
    jint value = env->GetIntField(obj, valueField);
    
    // Get string field (creates local reference)
    jstring name = (jstring)env->GetObjectField(obj, nameField);
    const char *nameStr = env->GetStringUTFChars(name, NULL);
    
    // Get array field
    jfloatArray array = (jfloatArray)env->GetObjectField(obj, arrayField);
    jfloat *arrayElements = env->GetFloatArrayElements(array, NULL);
    
    // Process data...
    
    // Release references (CRITICAL)
    env->ReleaseStringUTFChars(name, nameStr);
    env->ReleaseFloatArrayElements(array, arrayElements, JNI_ABORT);
    env->DeleteLocalRef(name);
    env->DeleteLocalRef(array);
    env->DeleteLocalRef(clazz);
}
```

### 2. Memory Management

#### Reference Management

**JNI Reference Types:**
1. **Local References**: Valid only in current thread and method
2. **Global References**: Valid across threads and method calls
3. **Weak Global References**: Allow garbage collection

**Best Practices:**
```cpp
class ReferenceManager {
private:
    // Cache global references
    static jclass gStringClass;
    static jclass gIntegerClass;
    static jmethodID gStringConstructor;
    
public:
    static void initialize(JNIEnv *env) {
        // Create global references (never garbage collected)
        jclass localStringClass = env->FindClass("java/lang/String");
        gStringClass = (jclass)env->NewGlobalRef(localStringClass);
        env->DeleteLocalRef(localStringClass);
        
        // Cache method IDs (never change during VM lifetime)
        gStringConstructor = env->GetMethodID(gStringClass, "<init>", "([C)V");
    }
    
    static void cleanup(JNIEnv *env) {
        // Delete global references
        if (gStringClass != NULL) {
            env->DeleteGlobalRef(gStringClass);
            gStringClass = NULL;
        }
    }
    
    // RAII wrapper for local references
    class LocalRefGuard {
    private:
        JNIEnv *mEnv;
        jobject mRef;
        
    public:
        LocalRefGuard(JNIEnv *env, jobject ref) : mEnv(env), mRef(ref) {}
        ~LocalRefGuard() {
            if (mRef != NULL) {
                mEnv->DeleteLocalRef(mRef);
            }
        }
        jobject get() { return mRef; }
    };
};
```

#### Native Memory Management

```cpp
class NativeMemoryManager {
public:
    // Allocate native memory
    static void* allocate(size_t size) {
        void *ptr = malloc(size);
        if (ptr == NULL) {
            // Handle out of memory
            throwNativeException("OutOfMemoryError");
            return NULL;
        }
        
        // Track allocation (for debugging)
        trackAllocation(ptr, size);
        return ptr;
    }
    
    // Deallocate native memory
    static void deallocate(void *ptr) {
        if (ptr != NULL) {
            trackDeallocation(ptr);
            free(ptr);
        }
    }
    
private:
    // Track allocations (for leak detection)
    static std::map<void*, size_t> sAllocations;
    static void trackAllocation(void *ptr, size_t size);
    static void trackDeallocation(void *ptr);
};
```

#### RAII Pattern for Automatic Cleanup

```cpp
class JNILocalRef {
private:
    JNIEnv *mEnv;
    jobject mRef;
    
public:
    JNILocalRef(JNIEnv *env, jobject ref) : mEnv(env), mRef(ref) {}
    
    ~JNILocalRef() {
        if (mRef != NULL && mEnv != NULL) {
            mEnv->DeleteLocalRef(mRef);
        }
    }
    
    // Non-copyable
    JNILocalRef(const JNILocalRef&) = delete;
    JNILocalRef& operator=(const JNILocalRef&) = delete;
    
    // Movable
    JNILocalRef(JNILocalRef&& other) : mEnv(other.mEnv), mRef(other.mRef) {
        other.mRef = NULL;
    }
    
    jobject get() const { return mRef; }
    operator jobject() const { return mRef; }
};
```

### 3. Error Handling and Exception Propagation

#### Exception Handling Framework

```cpp
class JNIExceptionHandler {
public:
    // Check for pending exception
    static bool checkException(JNIEnv *env) {
        if (env->ExceptionCheck()) {
            // Log exception
            env->ExceptionDescribe();
            return true;
        }
        return false;
    }
    
    // Clear exception
    static void clearException(JNIEnv *env) {
        env->ExceptionClear();
    }
    
    // Throw Java exception from native code
    static void throwException(JNIEnv *env, const char *className, 
                              const char *message) {
        jclass exceptionClass = env->FindClass(className);
        if (exceptionClass != NULL) {
            env->ThrowNew(exceptionClass, message);
            env->DeleteLocalRef(exceptionClass);
        }
    }
    
    // Throw common exceptions
    static void throwNullPointerException(JNIEnv *env, const char *message) {
        throwException(env, "java/lang/NullPointerException", message);
    }
    
    static void throwIllegalArgumentException(JNIEnv *env, const char *message) {
        throwException(env, "java/lang/IllegalArgumentException", message);
    }
    
    static void throwOutOfMemoryError(JNIEnv *env, const char *message) {
        throwException(env, "java/lang/OutOfMemoryError", message);
    }
    
    static void throwRuntimeException(JNIEnv *env, const char *message) {
        throwException(env, "java/lang/RuntimeException", message);
    }
    
    // Convert native error code to Java exception
    static void handleNativeError(JNIEnv *env, int errorCode, 
                                  const char *errorMessage) {
        switch (errorCode) {
            case ERROR_NULL_POINTER:
                throwNullPointerException(env, errorMessage);
                break;
            case ERROR_OUT_OF_MEMORY:
                throwOutOfMemoryError(env, errorMessage);
                break;
            case ERROR_INVALID_ARGUMENT:
                throwIllegalArgumentException(env, errorMessage);
                break;
            default:
                throwRuntimeException(env, errorMessage);
                break;
        }
    }
};
```

#### Safe JNI Call Wrapper

```cpp
template<typename Func>
jobject safeJNICall(JNIEnv *env, Func func) {
    jobject result = func();
    
    // Check for exceptions
    if (JNIExceptionHandler::checkException(env)) {
        // Cleanup and return NULL
        return NULL;
    }
    
    return result;
}

// Usage
JNIEXPORT jstring JNICALL
Java_JNIBridge_processString(JNIEnv *env, jobject thiz, jstring input) {
    // Check for null input
    if (input == NULL) {
        JNIExceptionHandler::throwNullPointerException(env, "Input string is null");
        return NULL;
    }
    
    // Get string chars
    const char *str = env->GetStringUTFChars(input, NULL);
    if (str == NULL) {
        // OutOfMemoryError already thrown
        return NULL;
    }
    
    // Process string
    std::string result = processNativeString(str);
    
    // Release string
    env->ReleaseStringUTFChars(input, str);
    
    // Check for exceptions during processing
    if (JNIExceptionHandler::checkException(env)) {
        return NULL;
    }
    
    // Create result string
    jstring resultStr = env->NewStringUTF(result.c_str());
    if (resultStr == NULL) {
        // OutOfMemoryError already thrown
        return NULL;
    }
    
    return resultStr;
}
```

### 4. Performance Optimization

#### Method ID and Field ID Caching

**Critical Performance Optimization:**

```cpp
class JNICache {
private:
    // Cache class references (global)
    static jclass gStringClass;
    static jclass gIntegerClass;
    static jclass gArrayListClass;
    
    // Cache method IDs (never change)
    static jmethodID gStringConstructor;
    static jmethodID gIntegerValueOf;
    static jmethodID gArrayListAdd;
    static jmethodID gArrayListGet;
    
    // Cache field IDs
    static jfieldID gIntegerValueField;
    
public:
    static void initialize(JNIEnv *env) {
        // Cache classes (create global references)
        jclass localStringClass = env->FindClass("java/lang/String");
        gStringClass = (jclass)env->NewGlobalRef(localStringClass);
        env->DeleteLocalRef(localStringClass);
        
        // Cache method IDs (expensive to look up)
        gStringConstructor = env->GetMethodID(gStringClass, "<init>", "([C)V");
        
        // Cache Integer class
        jclass localIntegerClass = env->FindClass("java/lang/Integer");
        gIntegerClass = (jclass)env->NewGlobalRef(localIntegerClass);
        env->DeleteLocalRef(localIntegerClass);
        
        gIntegerValueOf = env->GetStaticMethodID(gIntegerClass, "valueOf", 
                                                 "(I)Ljava/lang/Integer;");
        gIntegerValueField = env->GetFieldID(gIntegerClass, "value", "I");
    }
    
    static void cleanup(JNIEnv *env) {
        // Delete global references
        if (gStringClass != NULL) {
            env->DeleteGlobalRef(gStringClass);
            gStringClass = NULL;
        }
        if (gIntegerClass != NULL) {
            env->DeleteGlobalRef(gIntegerClass);
            gIntegerClass = NULL;
        }
    }
};
```

#### Minimize JNI Calls

**Batch Operations:**

```java
// Bad: Multiple JNI calls
public native void setValue1(int value);
public native void setValue2(int value);
public native void setValue3(int value);

// Good: Single JNI call with array
public native void setValues(int[] values);
```

```cpp
// Native implementation
JNIEXPORT void JNICALL
Java_JNIBridge_setValues(JNIEnv *env, jobject thiz, jintArray values) {
    jint *elements = env->GetIntArrayElements(values, NULL);
    jsize length = env->GetArrayLength(values);
    
    // Batch process (fast native code)
    for (jsize i = 0; i < length; i++) {
        processValue(elements[i]);
    }
    
    env->ReleaseIntArrayElements(values, elements, 0);
}
```

#### Use Critical Sections

**For performance-critical array access:**

```cpp
JNIEXPORT void JNICALL
Java_JNIBridge_processArrayCritical(JNIEnv *env, jobject thiz, jintArray array) {
    // Get critical array (blocks GC, fastest access)
    jint *elements = (jint*)env->GetPrimitiveArrayCritical(array, NULL);
    if (elements == NULL) {
        return; // OutOfMemoryError
    }
    
    jsize length = env->GetArrayLength(array);
    
    // Process array (must be fast, no JNI calls, no allocations)
    for (jsize i = 0; i < length; i++) {
        elements[i] = processValue(elements[i]);
    }
    
    // Release critical array (CRITICAL: must be called)
    env->ReleasePrimitiveArrayCritical(array, elements, 0);
}
```

### 5. Thread Safety Considerations

#### Thread Attachment

**JNI Environment is Thread-Local:**

```cpp
class JNIThreadManager {
public:
    // Get JNI environment for current thread
    static JNIEnv* getJNIEnv(JavaVM *vm) {
        JNIEnv *env = NULL;
        jint result = vm->GetEnv((void**)&env, JNI_VERSION_1_6);
        
        if (result == JNI_OK) {
            // Already attached
            return env;
        } else if (result == JNI_EDETACHED) {
            // Attach thread
            result = vm->AttachCurrentThread(&env, NULL);
            if (result == JNI_OK) {
                return env;
            }
        }
        
        return NULL; // Error
    }
    
    // Detach thread (call when thread exits)
    static void detachThread(JavaVM *vm) {
        vm->DetachCurrentThread();
    }
};

// Thread-safe wrapper
class ThreadSafeJNICall {
private:
    JavaVM *mVm;
    
public:
    ThreadSafeJNICall(JavaVM *vm) : mVm(vm) {}
    
    template<typename Func>
    auto call(Func func) -> decltype(func(std::declval<JNIEnv*>())) {
        JNIEnv *env = JNIThreadManager::getJNIEnv(mVm);
        if (env == NULL) {
            // Handle error
            return decltype(func(env))();
        }
        
        return func(env);
    }
};
```

#### Synchronization

**For shared resources:**

```cpp
class ThreadSafeJNIBridge {
private:
    JavaVM *mVm;
    std::mutex mMutex;
    
public:
    // Thread-safe method
    jint processValueThreadSafe(jint value) {
        std::lock_guard<std::mutex> lock(mMutex);
        
        JNIEnv *env = JNIThreadManager::getJNIEnv(mVm);
        if (env == NULL) {
            return -1;
        }
        
        // Perform synchronized operation
        return processValueInternal(env, value);
    }
};
```

#### Callback from Native Thread

```cpp
class NativeCallbackManager {
private:
    JavaVM *mVm;
    jobject mCallbackObject;
    jmethodID mCallbackMethod;
    
public:
    void callJavaCallback(jint result) {
        // Get JNI environment for current thread
        JNIEnv *env = JNIThreadManager::getJNIEnv(mVm);
        if (env == NULL) {
            return;
        }
        
        // Call Java method
        env->CallVoidMethod(mCallbackObject, mCallbackMethod, result);
        
        // Check for exceptions
        if (JNIExceptionHandler::checkException(env)) {
            // Handle exception
        }
        
        // Detach thread if needed (optional, depends on thread lifecycle)
        // JNIThreadManager::detachThread(mVm);
    }
};
```

## Step 4: Complete Implementation Example

### Java API

```java
public class JNIBridge {
    static {
        System.loadLibrary("native_lib");
    }
    
    // Initialize bridge (cache IDs, set up references)
    public static native void initialize();
    
    // Cleanup bridge (release global references)
    public static native void cleanup();
    
    // Efficient data transfer
    public native int processInt(int value);
    public native int[] processIntArray(int[] array);
    public native void processLargeData(ByteBuffer buffer, int size);
    public native DataObject processObject(DataObject obj);
    
    // Error handling
    public native String processString(String input) throws JNIException;
    
    // Thread-safe operations
    public native int processValueThreadSafe(int value);
    
    // Callback support
    public interface Callback {
        void onResult(int result);
    }
    
    public native void processAsync(Callback callback);
}
```

### Native Implementation

```cpp
#include <jni.h>
#include <string>
#include <mutex>
#include <map>

// Global JavaVM reference
static JavaVM *gVm = NULL;

// Cached references and method IDs
static jclass gStringClass = NULL;
static jclass gDataObjectClass = NULL;
static jmethodID gDataObjectConstructor = NULL;
static jfieldID gDataObjectValueField = NULL;

// Thread synchronization
static std::mutex gMutex;

// Initialize bridge
JNIEXPORT void JNICALL
Java_JNIBridge_initialize(JNIEnv *env, jclass clazz) {
    // Store JavaVM reference
    env->GetJavaVM(&gVm);
    
    // Cache classes
    jclass localStringClass = env->FindClass("java/lang/String");
    gStringClass = (jclass)env->NewGlobalRef(localStringClass);
    env->DeleteLocalRef(localStringClass);
    
    jclass localDataObjectClass = env->FindClass("com/example/DataObject");
    gDataObjectClass = (jclass)env->NewGlobalRef(localDataObjectClass);
    env->DeleteLocalRef(localDataObjectClass);
    
    // Cache method IDs
    gDataObjectConstructor = env->GetMethodID(gDataObjectClass, "<init>", "()V");
    gDataObjectValueField = env->GetFieldID(gDataObjectClass, "value", "I");
}

// Cleanup bridge
JNIEXPORT void JNICALL
Java_JNIBridge_cleanup(JNIEnv *env, jclass clazz) {
    if (gStringClass != NULL) {
        env->DeleteGlobalRef(gStringClass);
        gStringClass = NULL;
    }
    if (gDataObjectClass != NULL) {
        env->DeleteGlobalRef(gDataObjectClass);
        gDataObjectClass = NULL;
    }
}

// Process integer
JNIEXPORT jint JNICALL
Java_JNIBridge_processInt(JNIEnv *env, jobject thiz, jint value) {
    return value * 2;
}

// Process integer array
JNIEXPORT jintArray JNICALL
Java_JNIBridge_processIntArray(JNIEnv *env, jobject thiz, jintArray array) {
    if (array == NULL) {
        JNIExceptionHandler::throwNullPointerException(env, "Array is null");
        return NULL;
    }
    
    jint *elements = env->GetIntArrayElements(array, NULL);
    if (elements == NULL) {
        return NULL; // OutOfMemoryError
    }
    
    jsize length = env->GetArrayLength(array);
    
    // Process array
    for (jsize i = 0; i < length; i++) {
        elements[i] = elements[i] * 2;
    }
    
    env->ReleaseIntArrayElements(array, elements, 0);
    
    if (JNIExceptionHandler::checkException(env)) {
        return NULL;
    }
    
    return array;
}

// Process large data with direct buffer
JNIEXPORT void JNICALL
Java_JNIBridge_processLargeData(JNIEnv *env, jobject thiz, 
                                jobject buffer, jint size) {
    if (buffer == NULL) {
        JNIExceptionHandler::throwNullPointerException(env, "Buffer is null");
        return;
    }
    
    void *ptr = env->GetDirectBufferAddress(buffer);
    if (ptr == NULL) {
        JNIExceptionHandler::throwIllegalArgumentException(env, 
            "Buffer is not a direct buffer");
        return;
    }
    
    // Process data directly (no copying)
    processNativeData(ptr, size);
}

// Process object
JNIEXPORT jobject JNICALL
Java_JNIBridge_processObject(JNIEnv *env, jobject thiz, jobject obj) {
    if (obj == NULL) {
        JNIExceptionHandler::throwNullPointerException(env, "Object is null");
        return NULL;
    }
    
    // Get value field (using cached field ID if available)
    jint value = env->GetIntField(obj, gDataObjectValueField);
    
    if (JNIExceptionHandler::checkException(env)) {
        return NULL;
    }
    
    // Create new object
    jobject result = env->NewObject(gDataObjectClass, gDataObjectConstructor);
    if (result == NULL) {
        return NULL; // OutOfMemoryError
    }
    
    // Set value
    env->SetIntField(result, gDataObjectValueField, value * 2);
    
    if (JNIExceptionHandler::checkException(env)) {
        env->DeleteLocalRef(result);
        return NULL;
    }
    
    return result;
}

// Process string with error handling
JNIEXPORT jstring JNICALL
Java_JNIBridge_processString(JNIEnv *env, jobject thiz, jstring input) {
    if (input == NULL) {
        JNIExceptionHandler::throwNullPointerException(env, "Input string is null");
        return NULL;
    }
    
    const char *str = env->GetStringUTFChars(input, NULL);
    if (str == NULL) {
        return NULL; // OutOfMemoryError
    }
    
    // Process string
    std::string result = processNativeString(str);
    
    env->ReleaseStringUTFChars(input, str);
    
    if (JNIExceptionHandler::checkException(env)) {
        return NULL;
    }
    
    jstring resultStr = env->NewStringUTF(result.c_str());
    if (resultStr == NULL) {
        return NULL; // OutOfMemoryError
    }
    
    return resultStr;
}

// Thread-safe processing
JNIEXPORT jint JNICALL
Java_JNIBridge_processValueThreadSafe(JNIEnv *env, jobject thiz, jint value) {
    std::lock_guard<std::mutex> lock(gMutex);
    
    // Perform synchronized operation
    return processValueInternal(value);
}
```

## Step 5: Best Practices Summary

### Performance Optimization

1. **Cache Method IDs and Field IDs**: Lookup is expensive, cache them
2. **Use Direct Buffers**: For large data transfers (zero-copy)
3. **Minimize JNI Calls**: Batch operations when possible
4. **Use Critical Sections**: For performance-critical array access
5. **Avoid Unnecessary Conversions**: Work with native types when possible

### Memory Management

1. **Always Release References**: Local, global, and array elements
2. **Use RAII Patterns**: Automatic cleanup with destructors
3. **Track Allocations**: For debugging memory leaks
4. **Delete Local References**: Especially in loops
5. **Use Global References Sparingly**: Only when needed across threads

### Error Handling

1. **Check for Null**: Before dereferencing
2. **Check for Exceptions**: After every JNI call
3. **Provide Meaningful Messages**: For debugging
4. **Handle Out of Memory**: Gracefully
5. **Log Errors**: For production debugging

### Thread Safety

1. **Get JNIEnv Correctly**: Use GetEnv/AttachCurrentThread
2. **Synchronize Shared Resources**: Use mutexes when needed
3. **Detach Threads**: When native threads exit
4. **Avoid Sharing JNIEnv**: Each thread has its own
5. **Use Thread-Local Storage**: For thread-specific data

## Step 6: Common Pitfalls and Solutions

### Pitfall 1: Memory Leaks

**Problem**: Not releasing local references or array elements

**Solution**: Use RAII wrappers, always release in finally blocks

### Pitfall 2: Exception Handling

**Problem**: Not checking for exceptions after JNI calls

**Solution**: Check after every JNI call that can throw

### Pitfall 3: Thread Safety

**Problem**: Using JNIEnv from wrong thread

**Solution**: Always get JNIEnv for current thread

### Pitfall 4: Performance

**Problem**: Looking up method IDs repeatedly

**Solution**: Cache IDs during initialization

### Pitfall 5: Reference Management

**Problem**: Using local references across method boundaries

**Solution**: Use global references for cross-boundary access

## Conclusion

Designing a robust JNI bridge requires careful attention to:

1. **Efficient Data Transfer**: Minimize copying, use direct buffers, batch operations
2. **Memory Management**: Properly manage references, use RAII patterns, track allocations
3. **Error Handling**: Check exceptions, provide meaningful errors, handle gracefully
4. **Performance Optimization**: Cache IDs, minimize calls, use critical sections
5. **Thread Safety**: Proper thread attachment, synchronization, thread-local storage

**Key Design Principles:**
- **Cache Everything**: Method IDs, field IDs, class references
- **Release Everything**: Local references, array elements, string chars
- **Check Everything**: Null pointers, exceptions, error codes
- **Optimize Hot Paths**: Use direct buffers, critical sections, batch operations
- **Thread Safety First**: Always use correct JNIEnv, synchronize shared resources

This design demonstrates understanding of JNI internals, performance optimization, memory management, and thread safety—all critical for building production-grade Android framework components at Meta.

