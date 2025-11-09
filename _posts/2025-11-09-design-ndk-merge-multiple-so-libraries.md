---
layout: post
title: "Design an NDK System for Merging Multiple .so Libraries"
date: 2025-11-09
categories: [System Design, Android, NDK, Native Libraries, Build Systems, C/C++]
excerpt: "A comprehensive system design for building an NDK (Native Development Kit) system that can merge multiple .so (shared object) libraries, covering architecture, dependency resolution, symbol management, build integration, and best practices."
---

## Introduction

Android applications often use multiple native libraries (.so files) built with the Android NDK (Native Development Kit). Managing these libraries can become complex, especially when dealing with:
- Multiple third-party native libraries
- Dependency conflicts
- Large APK sizes
- Load time performance
- Symbol resolution issues

This post designs a system that can intelligently merge multiple .so libraries into optimized, consolidated libraries while maintaining functionality and resolving conflicts.

---

## Problem Statement

### Challenges with Multiple .so Libraries

**Current Problems:**
1. **APK Size**: Each .so library adds to APK size (especially with multiple ABIs)
2. **Load Time**: Loading multiple libraries increases startup time
3. **Dependency Conflicts**: Different libraries may require different versions of dependencies
4. **Symbol Conflicts**: Duplicate symbols across libraries
5. **Memory Overhead**: Multiple library mappings consume memory
6. **Complexity**: Managing multiple library dependencies is error-prone

### Goals

**Design a system that:**
- Merges multiple .so libraries into fewer consolidated libraries
- Resolves symbol conflicts and dependencies
- Maintains functionality and performance
- Reduces APK size
- Improves load time
- Integrates with existing build systems

---

## System Requirements

### Functional Requirements

1. **Library Merging**
   - Merge multiple .so files into single library
   - Support multiple architectures (arm64-v8a, armeabi-v7a, x86, x86_64)
   - Preserve all exported symbols
   - Handle static and dynamic linking

2. **Dependency Resolution**
   - Resolve transitive dependencies
   - Detect and resolve version conflicts
   - Handle circular dependencies
   - Support optional dependencies

3. **Symbol Management**
   - Detect symbol conflicts
   - Resolve duplicate symbols
   - Preserve symbol visibility
   - Handle weak symbols

4. **Build Integration**
   - Integrate with Gradle/CMake build systems
   - Support incremental builds
   - Cache merged libraries
   - Generate metadata

### Non-Functional Requirements

- **Performance**: Merging should not significantly slow builds
- **Reliability**: Merged libraries must work correctly
- **Compatibility**: Support existing NDK projects
- **Scalability**: Handle 10+ libraries efficiently
- **Maintainability**: Clear error messages and logs

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────┐
│      Source Code / Libraries            │
│  (C/C++ source, .so files, .a files)    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Library Analyzer                   │
│  (Parse .so, extract symbols, deps)    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Dependency Resolver                 │
│  (Build dependency graph, resolve)      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Conflict Detector                  │
│  (Detect symbol conflicts, versions)     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Library Merger                     │
│  (Merge .so files, resolve symbols)     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Optimizer                          │
│  (Strip unused symbols, optimize)       │
└──────────────┬──────────────────────────┐
               │
┌──────────────▼──────────────────────────┐
│      Merged .so Output                  │
│  (Single or few optimized libraries)    │
└─────────────────────────────────────────┘
```

### Component Design

**1. Library Analyzer**
- Parse ELF (Executable and Linkable Format) files
- Extract symbols (exported, imported)
- Extract dependencies (DT_NEEDED)
- Extract version information
- Build symbol table

**2. Dependency Resolver**
- Build dependency graph
- Resolve transitive dependencies
- Detect circular dependencies
- Resolve version conflicts
- Determine merge order

**3. Conflict Detector**
- Detect duplicate symbols
- Detect version conflicts
- Detect ABI incompatibilities
- Report conflicts with resolution suggestions

**4. Library Merger**
- Merge object files/sections
- Resolve symbol references
- Update relocation tables
- Merge dynamic symbol tables
- Handle constructors/destructors

**5. Optimizer**
- Remove unused symbols
- Strip debug symbols (optional)
- Optimize symbol tables
- Compress sections (optional)

---

## Detailed Component Design

### 1. Library Analyzer

**Responsibilities:**
- Parse ELF file format
- Extract metadata and symbols
- Build library dependency graph

**ELF File Structure:**
```
ELF Header
├── Program Headers (segments)
│   ├── LOAD segments (code, data)
│   └── DYNAMIC segment (dynamic linking info)
├── Section Headers
│   ├── .text (code)
│   ├── .data (initialized data)
│   ├── .bss (uninitialized data)
│   ├── .symtab (symbol table)
│   ├── .dynsym (dynamic symbol table)
│   └── .rel.* (relocation tables)
└── Section Data
```

**Analysis Process:**
```python
class LibraryAnalyzer:
    def analyze_library(self, so_file):
        # Parse ELF header
        elf = ELFFile(so_file)
        
        # Extract symbols
        symbols = self.extract_symbols(elf)
        
        # Extract dependencies
        dependencies = self.extract_dependencies(elf)
        
        # Extract version info
        versions = self.extract_versions(elf)
        
        # Extract exported/imported symbols
        exported = self.get_exported_symbols(elf)
        imported = self.get_imported_symbols(elf)
        
        return LibraryInfo(
            path=so_file,
            symbols=symbols,
            dependencies=dependencies,
            versions=versions,
            exported=exported,
            imported=imported
        )
```

**Symbol Extraction:**
- **Exported Symbols**: Symbols defined in this library
- **Imported Symbols**: Symbols needed from other libraries
- **Weak Symbols**: Can be overridden
- **Versioned Symbols**: Symbols with version information

### 2. Dependency Resolver

**Dependency Graph:**
```
libA.so
  ├── libB.so (version 1.0)
  └── libC.so (version 2.0)
      └── libB.so (version 1.1)  ← Conflict!
```

**Resolution Strategy:**

1. **Build Dependency Graph**
   ```python
   class DependencyResolver:
       def build_graph(self, libraries):
           graph = DependencyGraph()
           for lib in libraries:
               for dep in lib.dependencies:
                   graph.add_edge(lib, dep)
           return graph
   ```

2. **Topological Sort**
   - Determine merge order
   - Handle circular dependencies
   - Ensure dependencies merged before dependents

3. **Version Conflict Resolution**
   - **Latest Version**: Use newest version
   - **Strict Matching**: Require exact version match
   - **Compatible Versions**: Use compatible version
   - **User Override**: Allow manual specification

**Example:**
```python
def resolve_conflicts(self, graph):
    conflicts = []
    for node in graph.nodes:
        versions = graph.get_versions(node)
        if len(versions) > 1:
            # Resolve conflict
            resolved = self.resolve_version(versions)
            conflicts.append({
                'library': node,
                'versions': versions,
                'resolved': resolved
            })
    return conflicts
```

### 3. Conflict Detector

**Types of Conflicts:**

1. **Symbol Conflicts**
   - Same symbol defined in multiple libraries
   - Different implementations
   - Need to choose one or rename

2. **Version Conflicts**
   - Different versions of same library
   - ABI incompatibilities
   - Need version resolution

3. **ABI Conflicts**
   - Different ABIs (C++ ABI versions)
   - Incompatible calling conventions
   - Need ABI alignment

**Conflict Detection:**
```python
class ConflictDetector:
    def detect_symbol_conflicts(self, libraries):
        symbol_map = {}
        conflicts = []
        
        for lib in libraries:
            for symbol in lib.exported_symbols:
                if symbol.name in symbol_map:
                    # Conflict detected
                    conflicts.append({
                        'symbol': symbol.name,
                        'libraries': [symbol_map[symbol.name], lib],
                        'type': 'duplicate_definition'
                    })
                else:
                    symbol_map[symbol.name] = lib
        
        return conflicts
```

**Conflict Resolution Strategies:**

1. **First Wins**: Use first definition encountered
2. **Last Wins**: Use last definition encountered
3. **Strongest Symbol**: Prefer strong over weak symbols
4. **Rename**: Rename conflicting symbols
5. **User Choice**: Prompt user for resolution

### 4. Library Merger

**Merging Process:**

**Step 1: Extract Object Files**
```bash
# Extract object files from .so
objcopy --extract-section .text lib1.so lib1_text.o
objcopy --extract-section .data lib1.so lib1_data.o
```

**Step 2: Merge Sections**
- Combine .text sections
- Combine .data sections
- Combine .bss sections
- Update section addresses

**Step 3: Merge Symbol Tables**
- Combine symbol tables
- Resolve duplicate symbols
- Update symbol indices
- Preserve symbol visibility

**Step 4: Update Relocations**
- Update relocation entries
- Fix symbol references
- Update addresses

**Step 5: Merge Dynamic Sections**
- Combine DT_NEEDED entries
- Merge dynamic symbol tables
- Update version information

**Implementation:**
```python
class LibraryMerger:
    def merge_libraries(self, libraries, order):
        merged = MergedLibrary()
        
        # Merge in dependency order
        for lib in order:
            # Extract sections
            sections = self.extract_sections(lib)
            
            # Merge sections
            merged.add_sections(sections)
            
            # Merge symbols
            merged.merge_symbols(lib.symbols)
            
            # Update relocations
            merged.update_relocations(lib.relocations)
        
        # Resolve internal references
        merged.resolve_references()
        
        # Generate merged .so
        return merged.generate_so()
```

**Handling Constructors/Destructors:**
- Collect all `__attribute__((constructor))` functions
- Collect all `__attribute__((destructor))` functions
- Create init/fini arrays
- Ensure proper execution order

### 5. Optimizer

**Optimization Strategies:**

1. **Dead Code Elimination**
   - Remove unused functions
   - Remove unused data
   - Strip unreachable code

2. **Symbol Stripping**
   - Remove debug symbols (optional)
   - Remove local symbols
   - Keep only exported symbols

3. **Section Optimization**
   - Merge similar sections
   - Optimize alignment
   - Compress sections (optional)

4. **Size Optimization**
   - Remove duplicate strings
   - Optimize string tables
   - Compress metadata

**Implementation:**
```python
class LibraryOptimizer:
    def optimize(self, merged_lib):
        # Dead code elimination
        used_symbols = self.analyze_usage(merged_lib)
        merged_lib.remove_unused_symbols(used_symbols)
        
        # Strip debug symbols (if requested)
        if self.config.strip_debug:
            merged_lib.strip_debug_symbols()
        
        # Optimize sections
        merged_lib.optimize_sections()
        
        return merged_lib
```

---

## Build System Integration

### Gradle Integration

**Gradle Plugin:**
```groovy
// build.gradle
plugins {
    id 'com.android.application'
    id 'com.example.so-merger' version '1.0.0'
}

android {
    ndk {
        // NDK configuration
    }
}

soMerger {
    enabled true
    inputLibraries = [
        'lib1.so',
        'lib2.so',
        'lib3.so'
    ]
    outputLibrary = 'libmerged.so'
    conflictResolution = 'first_wins'
    stripDebugSymbols = true
    optimize = true
}
```

**Plugin Implementation:**
```kotlin
class SoMergerPlugin : Plugin<Project> {
    override fun apply(project: Project) {
        project.tasks.register("mergeSoLibraries", MergeSoTask::class.java) {
            it.inputLibraries.set(project.extensions.getByType(SoMergerExtension::class.java).inputLibraries)
            it.outputLibrary.set(project.extensions.getByType(SoMergerExtension::class.java).outputLibrary)
        }
    }
}
```

### CMake Integration

**CMake Function:**
```cmake
# CMakeLists.txt
include(SoMerger)

# Define libraries to merge
set(MERGE_LIBRARIES
    ${CMAKE_CURRENT_BINARY_DIR}/lib1.so
    ${CMAKE_CURRENT_BINARY_DIR}/lib2.so
    ${CMAKE_CURRENT_BINARY_DIR}/lib3.so
)

# Merge libraries
merge_so_libraries(
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/libmerged.so
    INPUTS ${MERGE_LIBRARIES}
    CONFLICT_RESOLUTION "first_wins"
    STRIP_DEBUG ON
    OPTIMIZE ON
)
```

---

## Dependency Management

### Dependency Graph

**Graph Structure:**
```python
class DependencyGraph:
    def __init__(self):
        self.nodes = {}  # library -> LibraryInfo
        self.edges = {}  # library -> [dependencies]
        self.reverse_edges = {}  # library -> [dependents]
    
    def add_library(self, lib):
        self.nodes[lib.name] = lib
        self.edges[lib.name] = []
        self.reverse_edges[lib.name] = []
    
    def add_dependency(self, lib, dep):
        self.edges[lib.name].append(dep.name)
        self.reverse_edges[dep.name].append(lib.name)
```

**Topological Sort:**
```python
def topological_sort(self, graph):
    in_degree = {node: len(graph.reverse_edges[node]) 
                 for node in graph.nodes}
    queue = [node for node, degree in in_degree.items() if degree == 0]
    result = []
    
    while queue:
        node = queue.pop(0)
        result.append(node)
        
        for neighbor in graph.edges[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    if len(result) != len(graph.nodes):
        raise CircularDependencyError("Circular dependency detected")
    
    return result
```

### Version Resolution

**Semantic Versioning:**
- Major.Minor.Patch (e.g., 1.2.3)
- Compare versions
- Determine compatibility

**Resolution Strategies:**
```python
def resolve_version(self, versions, strategy='latest'):
    if strategy == 'latest':
        return max(versions, key=Version)
    elif strategy == 'strict':
        if len(set(versions)) > 1:
            raise VersionConflictError(versions)
        return versions[0]
    elif strategy == 'compatible':
        return self.find_compatible_version(versions)
```

---

## Symbol Management

### Symbol Resolution

**Symbol Types:**
- **Global Symbols**: Exported symbols
- **Local Symbols**: Internal symbols
- **Weak Symbols**: Can be overridden
- **Versioned Symbols**: Symbols with version info

**Resolution Process:**
```python
class SymbolResolver:
    def resolve_symbols(self, libraries, conflicts):
        symbol_table = {}
        
        for lib in libraries:
            for symbol in lib.exported_symbols:
                if symbol.name in conflicts:
                    # Resolve conflict
                    resolved = self.resolve_conflict(symbol, conflicts[symbol.name])
                    symbol_table[symbol.name] = resolved
                else:
                    symbol_table[symbol.name] = symbol
        
        return symbol_table
```

### Symbol Renaming

**When to Rename:**
- Duplicate symbols with different implementations
- Namespace conflicts
- User-specified renaming

**Renaming Strategy:**
```python
def rename_symbol(self, symbol, prefix):
    new_name = f"{prefix}_{symbol.name}"
    # Update all references
    self.update_references(symbol.name, new_name)
    return Symbol(new_name, symbol.type, symbol.value)
```

---

## Performance Considerations

### Build Time

**Optimization:**
- **Incremental Merging**: Only merge changed libraries
- **Caching**: Cache merged libraries
- **Parallel Processing**: Merge libraries in parallel
- **Lazy Analysis**: Analyze only when needed

**Caching Strategy:**
```python
class MergeCache:
    def get_cache_key(self, libraries):
        # Hash of library paths and modification times
        return hashlib.md5(
            '|'.join(f"{lib.path}:{lib.mtime}" for lib in libraries)
        ).hexdigest()
    
    def get_cached(self, key):
        cache_file = f"{CACHE_DIR}/{key}.so"
        if os.path.exists(cache_file):
            return cache_file
        return None
```

### Runtime Performance

**Load Time:**
- Single library loads faster than multiple
- Reduced dynamic linking overhead
- Fewer file I/O operations

**Memory Usage:**
- Single memory mapping vs multiple
- Reduced memory fragmentation
- Better cache locality

**Symbol Resolution:**
- Faster symbol lookup (single symbol table)
- Reduced dynamic linking overhead
- Better optimization opportunities

---

## Use Cases

### Use Case 1: Third-Party Libraries

**Scenario:**
- App uses multiple third-party native libraries
- Each library has its own dependencies
- Want to reduce APK size and load time

**Solution:**
- Merge all third-party libraries into single library
- Resolve dependency conflicts
- Optimize merged library

### Use Case 2: Modular Architecture

**Scenario:**
- App has modular architecture
- Each module has native code
- Want to consolidate for production

**Solution:**
- Merge module libraries per feature
- Keep modules separate during development
- Merge for release builds

### Use Case 3: Dependency Reduction

**Scenario:**
- Multiple libraries depend on same base library
- Want to avoid loading base library multiple times

**Solution:**
- Merge base library into dependents
- Eliminate separate base library
- Reduce total library count

---

## Implementation Approaches

### Approach 1: Link-Time Merging

**Process:**
1. Extract object files from .so
2. Link object files together
3. Generate new .so

**Tools:**
- `objcopy`: Extract sections
- `ld`: Link object files
- Custom linker scripts

**Pros:**
- Full control over linking
- Can optimize aggressively
- Handles all symbol types

**Cons:**
- Complex implementation
- May break some libraries
- Requires deep ELF knowledge

### Approach 2: Runtime Merging

**Process:**
1. Load libraries at runtime
2. Merge symbol tables
3. Redirect symbol lookups

**Pros:**
- Simpler implementation
- No build-time changes
- Works with existing libraries

**Cons:**
- Runtime overhead
- May not reduce APK size
- Complex symbol redirection

### Approach 3: Source-Level Merging

**Process:**
1. Extract source code (if available)
2. Compile together
3. Generate single library

**Pros:**
- Best optimization opportunities
- Full control
- No symbol conflicts

**Cons:**
- Requires source code
- May not be possible for third-party
- More complex build

**Recommended: Link-Time Merging**
- Best balance of control and compatibility
- Can handle binary-only libraries
- Good optimization opportunities

---

## Error Handling

### Common Errors

1. **Symbol Conflicts**
   - Error: Duplicate symbol definitions
   - Resolution: Rename or choose one
   - User Action: Specify conflict resolution

2. **Version Conflicts**
   - Error: Incompatible library versions
   - Resolution: Use compatible version
   - User Action: Update dependencies

3. **Circular Dependencies**
   - Error: Circular dependency detected
   - Resolution: Break cycle or merge together
   - User Action: Refactor dependencies

4. **ABI Incompatibilities**
   - Error: Different ABIs detected
   - Resolution: Use compatible ABI
   - User Action: Rebuild with same ABI

### Error Reporting

**Structured Errors:**
```json
{
    "type": "symbol_conflict",
    "symbol": "some_function",
    "libraries": ["lib1.so", "lib2.so"],
    "suggestions": [
        "Rename symbol in lib1.so",
        "Rename symbol in lib2.so",
        "Use first definition"
    ]
}
```

---

## Testing Strategy

### Unit Tests

**Test Cases:**
- Symbol extraction
- Dependency resolution
- Conflict detection
- Merging correctness

### Integration Tests

**Test Cases:**
- Merge real libraries
- Verify functionality
- Performance benchmarks
- APK size reduction

### Validation

**Validation Steps:**
1. **Symbol Verification**: All symbols present
2. **Functionality Test**: Run test suite
3. **Performance Test**: Benchmark load time
4. **Size Verification**: Check APK size reduction

---

## Best Practices

### 1. Library Organization

**✅ Do:**
- Group related libraries
- Merge libraries with same dependencies
- Keep core libraries separate
- Document merge decisions

**❌ Don't:**
- Merge unrelated libraries
- Merge libraries with conflicting ABIs
- Merge debug and release libraries
- Ignore version conflicts

### 2. Conflict Resolution

**Guidelines:**
- Prefer explicit resolution
- Document resolution decisions
- Test after merging
- Version control merged libraries

### 3. Performance

**Optimization:**
- Enable optimization flags
- Strip debug symbols in release
- Use incremental builds
- Cache merged libraries

### 4. Maintenance

**Best Practices:**
- Regular dependency updates
- Monitor for new conflicts
- Keep merge configuration simple
- Document merge process

---

## Comparison with Alternatives

### Alternative 1: Static Linking

**Comparison:**
- **Static Linking**: Link at compile time
- **Our Approach**: Merge shared libraries
- **Trade-off**: Static = larger binary, no runtime dependencies

### Alternative 2: Dynamic Loading

**Comparison:**
- **Dynamic Loading**: Load libraries at runtime
- **Our Approach**: Merge at build time
- **Trade-off**: Dynamic = flexible, but more overhead

### Alternative 3: App Bundles

**Comparison:**
- **App Bundles**: Split by ABI/device
- **Our Approach**: Merge libraries
- **Trade-off**: Can combine both approaches

---

## Future Enhancements

1. **Intelligent Merging**
   - Analyze usage patterns
   - Merge only used symbols
   - Profile-guided optimization

2. **Cross-Platform Support**
   - Support iOS (.dylib)
   - Support Linux (.so)
   - Support Windows (.dll)

3. **Advanced Optimization**
   - Link-time optimization (LTO)
   - Dead code elimination
   - Function reordering

4. **Better Tooling**
   - Visual dependency graph
   - Interactive conflict resolution
   - Performance profiling

---

## Conclusion

Designing an NDK system to merge multiple .so libraries requires:

**Key Components:**
1. **Library Analyzer**: Parse and understand libraries
2. **Dependency Resolver**: Resolve dependencies and conflicts
3. **Conflict Detector**: Identify and resolve conflicts
4. **Library Merger**: Merge libraries correctly
5. **Optimizer**: Optimize merged libraries

**Key Design Decisions:**
- **Link-Time Merging**: Best balance of control and compatibility
- **Dependency Resolution**: Topological sort with conflict resolution
- **Symbol Management**: Rename or choose strategy for conflicts
- **Build Integration**: Gradle/CMake plugins for seamless integration

**Benefits:**
- Reduced APK size
- Faster load time
- Simplified dependency management
- Better optimization opportunities

**Challenges:**
- Symbol conflict resolution
- Version compatibility
- ABI alignment
- Testing merged libraries

This system enables efficient management of multiple native libraries while maintaining functionality and improving performance.

