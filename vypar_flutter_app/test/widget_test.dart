import 'package:flutter_test/flutter_test.dart';
import 'package:vypar_flutter_app/main.dart';

void main() {
  testWidgets('App loads splash screen', (WidgetTester tester) async {
    await tester.pumpWidget(const VyparApp());
    expect(find.text('Vypar'), findsOneWidget);
  });
}
